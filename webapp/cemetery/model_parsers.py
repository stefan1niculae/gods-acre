from typing import Optional, Tuple, Dict, Callable, Any, List
from copy import deepcopy
import logging
from collections import namedtuple
from itertools import zip_longest
from functools import partial

from django.forms.models import model_to_dict

import numpy as np
import pandas as pd
from dateutil.parser import parse
from datetime import datetime

from .models import Spot, Operation, Deed, OwnershipReceipt, Owner, Construction, Authorization, Company
from .utils import title_case, year_shorthand_to_full, reverse_dict, filter_dict, show_dict, map_dict, parse_nr_year, \
    keep_only, display_change_link


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def natural_getsert(model) -> Callable:  # takes a django model
    """ getsert = get or insert; natural = using natural key """
    def handler(identifier: Optional[str]):  # returns an entity
        if identifier is None:
            return None

        # prepare the natural key into a dict that can be passed to __init__
        natural_key = model.objects.prepare_natural_key(identifier)

        try:
            # retrieve by natural key
            entity = model.objects.get_by_natural_key(**natural_key)
        except model.DoesNotExist:
            # create if it doesn't exist
            entity = model(**natural_key)
            entity.save()
        return entity

    return handler


def relational_get(model, fields: Dict, relational_keys: [str]):
    try:
        query_fields = {(k + '__in' if k in relational_keys else k): v for k, v in fields.items()}
        entities = model.objects.filter(**query_fields)
    except Exception:
        raise ValueError(f'Filter by {{{show_dict(fields)}}}')

    if len(entities) != 1:  # don't use get as it throws an error on multiple matches, but it is in fact not an error
        return None

    entity = entities[0]
    lengths_equal = all(getattr(entity, f).count() == len(fields[f]) for f in fields)  # __in can return partials
    if not lengths_equal:
        return None

    return entity


def multiple(single_parser: Callable, separator: str=',', required=False) -> Callable:
    """ makes a parser that works on a single element work on a list of elements, split by a separator """
    def handler(inp: Optional[str]) -> Optional[List]:  # returns an entity
        if inp is None:
            if required:
                raise ValueError('Expected at least one element for multiple parsing')
            return []
        return [single_parser(elem) for elem in str(inp).split(separator)]
    return handler

def parse_date(arg) -> Optional[datetime]:
    """
    Parse the date contained in the string
    
    Args:
        arg (str | int | None): what to parse 

    Returns:
        datetime: parsed datetime object
        
    Examples:
        >>> parse_date('1994')
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date("'94")
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date('94')
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date("'17")
        datetime.datetime(2017, 1, 1, 0, 0)
        
        >>> parse_date('17')  # ambiguous interpreted as year
        datetime.datetime(2017, 1, 1, 0, 0)
        
        >>> parse_date('24.01.1994')  # infer day first
        datetime.datetime(1994, 1, 24, 0, 0)

        >>> parse_date('01.24.1994')  # infer month first
        datetime.datetime(1994, 1, 24, 0, 0)

        >>> parse_date('05.01.1994')  # ambiguous interpreted as month first
        datetime.datetime(1994, 1, 5, 0, 0)

        >>> parse_date('18 07 2017')  # different separator
        datetime.datetime(2017, 7, 18, 0, 0)

        >>> parse_date(None)

        >>> parse_date(2017)  # ints work as well
        datetime.datetime(2017, 1, 1, 0, 0)

        >>> parse_date(94)  # ints work as well
        datetime.datetime(1994, 1, 1, 0, 0)

        >>> parse_date('06')
        datetime.datetime(2006, 1, 1, 0, 0)

        >>> parse_date('6')
        datetime.datetime(2006, 1, 1, 0, 0)
        
        >>> parse_date('00')
        datetime.datetime(2000, 1, 1, 0, 0)
    """

    if arg is None:
        return None

    str_arg = str(arg)  # convert ints
    try:
        int_arg = int(str_arg.replace("'", ""))    # to be able to convert '17
        int_arg = year_shorthand_to_full(int_arg)  # to correctly assess 17 as the year 2017 instead of day 17
        str_arg = str(int_arg)
    except ValueError:
        pass  # it's ok if it's not an int

    return parse(str_arg,
                 dayfirst=True,  # for ambiguities like `10.10.1994`
                 default=datetime(year=2000, month=1, day=1))   # when only the year is given, set to Jan 1st

def translate(dictionary: Dict[str, str], default=None):
    def handler(string: Optional[str]) -> str:
        try:
            return dictionary[string]
        except KeyError:
            if string is None:  # no value entered
                return default
            raise ValueError(f'Wrong value: {string} is not one of {", ".join(dictionary.keys())}')
    return handler

def as_is(x):
    """ identity function """
    return x

def prepare_deed_fields(parsed_fields: Dict[str, Any]) -> Dict[str, Any]:
        """ takes keys: deed_id, spots, receipts_ids, values, owners, cancel_reason 
            returns keys: number, year, cancel_reason, spots, owners, receipts """
        number, year = parsed_fields['deed_id']

        receipt_ids = parsed_fields['receipt_ids']
        values      = parsed_fields['values']
        if len(values) > len(receipt_ids):  # make sure there no more than one value per receipt id
            raise ValueError(f'More values ({len(values)} than receipts ({len(receipt_ids)})')
        receipts = [OwnershipReceipt.objects.get_or_create(
                        number=nr, year=yr, defaults={'value': val})[0]  # returns entity, created_now
                    for (nr, yr), val in zip_longest(receipt_ids, values)]  # missing values will be None

        return {
            'number':        number,
            'year':          year,
            'cancel_reason': parsed_fields['cancel_reason'],
            'spots':         parsed_fields['spots'],
            'owners':        parsed_fields['owners'],
            'receipts':      receipts,
        }

ModelMetadata = namedtuple('ModelMetadata',
                           'model sheet_name column_renames field_parsers prepare_fields '
                           'identifying_fields relational_fields')
"""
    model (django.db.models.Model): class of the resulting object
    sheet_name (str): excel sheet name
    column_renames (dict<str: str>): code_field_name: excel_column_name
    field_parsers (dict<str: str -> Any>): type of the field - an entry for a field takes the cell content and 
        produces a value (eg: title-cased name, spot object from its textual representation)
    identifying_fields ([str]): fields that should be present in `get_or_create` args, others instead in defaults kwarg
        eg: name Owner (but not address or phone)
    prepare_fields (dict<str: Any> -> dict<str: Any>): change the fields values/keys to fit the model's __init__ -
        takes dict of {input_field: parsed_value} and transforms it into {model_field: value} (eg: combine values and
        receipt_identifiers into receipts or split deed_identifier into number and year)
    relational_fields ([str]): fields that need to be assigned after a the object received its pk (eg: owners for deed)
"""

operation_type_translations = {
    'inhumare':     Operation.BURIAL,
    'dezhumare':    Operation.EXHUMATION,
}

deed_cancel_reason_translations = {
    'proprietar decedat': Deed.OWNER_DEAD,
    'donat':              Deed.DONATED,
    'pierdut':            Deed.LOST,
}

construction_type_translations = {
    'cavou':   Construction.TOMB,
    'bordura': Construction.BORDER,
}

MODELS_METADATA = [
    ModelMetadata(
        model=Operation,
        sheet_name='Operatii',
        column_renames={
          'type':     'Tip',
          'deceased': 'Decedat',
          'spot':     'Loc veci',
          'date':     'Data',
          'exhumation_written_report': 'Exhumare PV',
          'remains_brought_from':      'Adus oseminte din',
        },
        field_parsers={
          'type':     translate(operation_type_translations, default=Operation.BURIAL),
          'deceased': title_case,
          'spot':     natural_getsert(Spot),
          'date':     parse_date,
          'exhumation_written_report': as_is,
          'remains_brought_from':      as_is
        },
        prepare_fields=as_is,
        identifying_fields={'type', 'deceased', 'spot', 'date'},
        relational_fields=set(),
    ),

    ModelMetadata(
        model=Deed,
        sheet_name='Acte concesiune',
        column_renames={
            'deed_id':       'Act',
            'spots':         'Locuri veci',
            'receipt_ids':   'Chitante',
            'values':        'Valori',
            'owners':        'Proprietari',
            'cancel_reason': 'Motiv anulare',
        },
        field_parsers={
            'deed_id':       parse_nr_year,
            'spots':         multiple(natural_getsert(Spot), required=True),
            'receipt_ids':   multiple(parse_nr_year),
            'values':        multiple(float),
            'owners':        multiple(natural_getsert(Owner)),
            'cancel_reason': translate(deed_cancel_reason_translations),
        },
        prepare_fields=prepare_deed_fields,
        identifying_fields={'number', 'year'},
        relational_fields={'spots', 'owners', 'receipts'},
    ),

    ModelMetadata(
        model=Owner,
        sheet_name='Proprietari',
        column_renames={
            'name':     'Nume',
            'address':  'Adresa',
            'city':     'Localitate',
            'phone':    'Telefon',
        },
        field_parsers={
            'name':     title_case,
            'address':  title_case,
            'city':     title_case,
            'phone':    partial(keep_only, condition=str.isdigit),
        },
        prepare_fields=as_is,
        identifying_fields={'name'},
        relational_fields=set(),
    ),

    ModelMetadata(
        model=Construction,
        sheet_name='Constructii',
        column_renames={
            'type':           'Tip',
            'spots':          'Locuri veci',
            'authorizations': 'Autorizatii',
            'owner_builder':  'Constructor proprietar',
            'company':        'Companie',
        },
        field_parsers={
            'type':           translate(construction_type_translations),
            'spots':          multiple(natural_getsert(Spot), required=True),
            'authorizations': multiple(natural_getsert(Authorization)),
            'owner_builder':  natural_getsert(Owner),
            'company':        natural_getsert(Company),
        },
        prepare_fields=as_is,
        identifying_fields={'type', 'spots'},
        relational_fields={'spots', 'authorizations', 'company', 'owner_builder'}
    )

]

RowFeedback = namedtuple('RowFeedback', 'status info additional')
"""
    status (str):       fail            | add / duplicate
    info (str):         failure cause   | entity link
    additional (str):   exception       | fields as dict
"""

def entity2dict_str(entity) -> str:
    d = model_to_dict(entity)
    return '{' + show_dict(d) + '}'

def parse_row(row, metadata) -> Tuple[str, str, str]:
    model = metadata.model
    model_name = model.__name__

    # 1. parse fields
    parsed_fields = {}
    for field, parser in metadata.field_parsers.items():
        try:
            parsed_fields[field] = parser(row[field])
        except Exception as error:
            info = f'Parse column "{field}": {row[field]}'
            return 'fail', info, repr(error)  # repr instead of str to get the exception type as well

    # 2. prepare the parsed fields
    try:
        prepared_fields = metadata.prepare_fields(parsed_fields)
    except Exception as error:
        info = f'Prepare the parsed fields {{{show_dict(parsed_fields)}}}'
        return 'fail', info, repr(error)

    # 3. use the prepared fields to build the model
    try:
        # create the entity (if it doesn't already exist)
        identif_rel = metadata.identifying_fields & metadata.relational_fields  # identifying and relational
        identif_items = filter_dict(prepared_fields, metadata.identifying_fields)
        identif_non_rel_items = filter_dict(identif_items, metadata.relational_fields, inverse=True)

        if not identif_rel:
            # non identifiable and non relational
            safe_defaults = filter_dict(prepared_fields,
                                        metadata.identifying_fields | metadata.relational_fields, inverse=True)
            entity, created_now  = model.objects.get_or_create(**identif_items, defaults=safe_defaults)

        else:  # model has identifying and relational fields
            identif_rel_items = filter_dict(prepared_fields, identif_rel)
            entity = relational_get(model, identif_rel_items, metadata.relational_fields)
            if not entity:  # there is not an entity that matches exactly the relational fields
                entity = model(**identif_non_rel_items)
                entity.save()
                created_now = True
            else:
                created_now = False

    except Exception as error:
        info = f'Get/create {model_name} with init {{{show_dict(identif_items)}}}'
        return 'fail', info, repr(error)

    if not created_now:  # entity already existed
        for field, value in prepared_fields.items():
            try:
                setattr(entity, field, value)
            except Exception as error:
                info = f'Update on duplicate "{field}": {{value}}'
                return 'fail', info, repr(error)

        try:
            entity.save()
        except Exception as error:
            info = f'Save after updating fields on found-duplicate {entity}'
            return 'fail', info, repr(error)
        return 'duplicate', display_change_link(entity), entity2dict_str(entity)

    # 4. save the entity
    try:
        entity.save()
    except Exception as error:
        info = f'Save {model_name}: {entity}'  # TODO check if this provides enough info
        return 'fail', info, repr(error)

    # 5. set relational fields
    for field in metadata.relational_fields:
        try:
            setattr(entity, field, prepared_fields[field])
        except Exception as error:
            info = f'Set relational field {field}: {prepared_fields[field]}'
            return 'fail', info, repr(error)
    try:
        entity.save()
    except Exception as error:
        info = f'Save after setting relational fields on {entity}'
        return 'fail', info, repr(error)

    # finally success
    return 'add', display_change_link(entity), entity2dict_str(entity)


def parse_sheet(file, metadata) -> [RowFeedback]:
    sheet = pd.read_excel(file, sheetname=metadata.sheet_name)
    sheet = sheet.rename(columns=reverse_dict(metadata.column_renames))  # translate
    sheet = sheet.replace({np.nan: None})  # mostly not numerical data: None is easier to work with

    return [RowFeedback(*parse_row(row, metadata)) for _, row in sheet.iterrows()]

def status_counts(feedbacks: [RowFeedback]) -> Dict[str, int]:
    statuses = [f.status for f in feedbacks]
    return {status: statuses.count(status) for status in ['fail', 'duplicate', 'add']}

def parse_file(file):
    # send a copy of the file because the document gets consumed after reading a sheet
    feedbacks = {metadata.sheet_name: parse_sheet(deepcopy(file), metadata) for metadata in MODELS_METADATA}
    return feedbacks, map_dict(feedbacks, status_counts)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
