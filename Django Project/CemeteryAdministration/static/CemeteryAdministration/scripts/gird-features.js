// Generated by CoffeeScript 1.10.0
(function() {
  var addTableSuperHeaders, changeIcons, initJsGrid;

  $(function() {
    var paymentsTable;
    paymentsTable = $(".jsgrid");
    initJsGrid(paymentsTable);
    return changeIcons();
  });

  this.tableConfigs = {
    spotFields: [
      {
        name: "parcel",
        title: "Parcel",
        type: "text"
      }, {
        name: "row",
        title: "Row",
        type: "text"
      }, {
        name: "column",
        title: "Column",
        type: "text"
      }
    ],
    controlFields: [
      {
        type: "control",
        editButton: false,
        modeSwitchButton: true
      }
    ],
    payments: {
      url: "/payments/api/",
      fields: [
        {
          name: "year",
          title: "Year Paid",
          type: "number",
          align: "left",
          headercss: "left-aligned-header"
        }, {
          name: "value",
          title: "Paid Amount",
          type: "number",
          align: "left",
          headercss: "left-aligned-header"
        }, {
          name: "receiptNumber",
          title: "Receipt Nr",
          type: "number",
          headercss: "left-aligned-header"
        }, {
          name: "receiptYear",
          title: "Receipt Year",
          type: "number",
          headercss: "left-aligned-header"
        }
      ]
    },
    burials: {
      url: "/burials/api/",
      fields: [
        {
          name: "firstName",
          title: "First Name",
          type: "text"
        }, {
          name: "lastName",
          title: "Last Name",
          type: "text"
        }, {
          name: "type",
          title: "Type",
          type: "select",
          items: [
            {
              Text: "",
              Value: ""
            }, {
              Text: "Burial",
              Value: "bral"
            }, {
              Text: "Exhumation",
              Value: "exhm"
            }
          ],
          textField: "Text",
          valueField: "Value",
          align: "left",
          headercss: "left-aligned-header"
        }, {
          name: "year",
          title: "Year",
          type: "number"
        }, {
          name: "note",
          title: "Notes",
          type: "text"
        }
      ]
    },
    maintenance: {
      url: "/maintenance_jsgrid/api/",
      fields: [
        {
          name: "year",
          title: "Year",
          type: "number"
        }, {
          name: "isKept",
          title: "Kept",
          type: "checkbox",
          headercss: "left-aligned-header"
        }, {
          name: "firstName",
          title: "First Name",
          type: "text",
          inserting: false,
          editing: false
        }, {
          name: "lastName",
          title: "Last Name",
          type: "text",
          inserting: false,
          editing: false
        }
      ]
    },
    ownerships: {
      url: "/ownerships_jsgrid/api/",
      fields: [
        {
          name: "firstName",
          title: "First Name",
          type: "text"
        }, {
          name: "lastName",
          title: "Last Name",
          type: "text"
        }, {
          name: "phone",
          title: "Phone",
          type: "text"
        }, {
          name: "deedNumber",
          title: "Deed Nr",
          type: "number"
        }, {
          name: "deedYear",
          title: "Deed Year",
          type: "number"
        }, {
          name: "sharingSpots",
          title: "On Same Deed",
          type: "text",
          inserting: false,
          editing: false
        }, {
          name: "receiptNumber",
          title: "Receipt Nr",
          type: "number"
        }, {
          name: "receiptYear",
          title: "Receipt Year",
          type: "number"
        }, {
          name: "receiptValue",
          title: "Amount Paid",
          type: "number"
        }
      ]
    },
    constructions: {
      url: "/constructions_jsgrid/api/",
      fields: [
        {
          name: "constructionType",
          title: "Type",
          type: "select",
          items: [
            {
              Text: "",
              Value: ""
            }, {
              Text: "Border",
              Value: "brdr"
            }, {
              Text: "Tomb",
              Value: "tomb"
            }
          ],
          textField: "Text",
          valueField: "Value",
          align: "left",
          headercss: "left-aligned-header"
        }, {
          name: "builder",
          title: "Builder",
          type: "text"
        }, {
          name: "authorizationNumber",
          title: "Auth Nr",
          type: "number"
        }, {
          name: "authorizationYear",
          title: "Auth Year",
          type: "number"
        }, {
          name: "sharingAuthorization",
          title: "On Same Auth",
          type: "text",
          inserting: false,
          editing: false
        }
      ]
    }
  };

  initJsGrid = function(table) {
    var configs;
    configs = tableConfigs[table.attr("id")];
    return table.jsGrid({
      width: "100%",
      fields: tableConfigs.spotFields.concat(configs.fields, tableConfigs.controlFields),
      controller: {
        loadData: function(filter) {
          var d, key, val;
          d = $.Deferred();
          for (key in filter) {
            val = filter[key];
            if (val === 0 && key.match(/(number|year|value)$/i)) {
              console.log("key = " + key + ", val = " + val);
              filter[key] = '';
            }
          }
          console.log("filter = " + (JSON.stringify(filter, null, 2)));
          $.ajax({
            type: "GET",
            url: configs.url,
            data: filter
          }).done(function(result) {
            return d.resolve($.map(result, function(item) {
              return $.extend(item.fields, {
                id: item.pk
              });
            }));
          });
          return d.promise();
        },
        insertItem: function(item) {
          return $.ajax({
            type: "POST",
            url: configs.url,
            data: item
          });
        },
        updateItem: function(item) {
          return $.ajax({
            type: "PUT",
            url: "" + configs.url + item.id,
            data: item
          });
        },
        deleteItem: function(item) {
          return $.ajax({
            type: "DELETE",
            url: "" + configs.url + item.id
          });
        }
      },
      heading: true,
      filtering: true,
      inserting: true,
      editing: true,
      selecting: true,
      sorting: true,
      paging: true,
      autoload: true,
      pageSize: 25,
      pageButtonCount: 5,
      pagerFormat: "{first} {prev} {pages} {next} {last} ( {itemCount} results )",
      pagePrevText: "<i class=\"fa fa-chevron-left\"></i>",
      pageNextText: "<i class=\"fa fa-chevron-right\"></i>",
      pageFirstText: "First",
      pageLastText: "Last"
    });
  };

  addTableSuperHeaders = function(table) {
    return $("<tr class=\"jsgrid-header-row super-header-row\">\n  <th colspan=\"3\">Spot</th>\n  <th colspan=\"2\">Payment</th>\n  <th colspan=\"2\">Receipt</th>\n</tr>").prependTo(table);
  };

  changeIcons = function() {};

}).call(this);

//# sourceMappingURL=gird-features.js.map
