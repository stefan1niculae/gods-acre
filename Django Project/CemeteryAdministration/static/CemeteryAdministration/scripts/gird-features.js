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
        title: "Spot Parcel",
        type: "text"
      }, {
        name: "row",
        title: "Spot Row",
        type: "text"
      }, {
        name: "column",
        title: "Spot Column",
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
          name: "parcel",
          title: "Spot Parcel",
          type: "text"
        }, {
          name: "row",
          title: "Spot Row",
          type: "text"
        }, {
          name: "column",
          title: "Spot Column",
          type: "text"
        }, {
          name: "year",
          title: "Year Paid",
          type: "text",
          align: "left",
          headercss: "left-aligned-header"
        }, {
          name: "value",
          title: "Paid Amount",
          type: "text",
          align: "left",
          headercss: "left-aligned-header"
        }, {
          name: "receiptNumber",
          title: "Receipt Nr",
          type: "text",
          headercss: "left-aligned-header"
        }, {
          name: "receiptYear",
          title: "Receipt Year",
          type: "text",
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
          type: "text"
        }, {
          name: "note",
          title: "Notes",
          type: "text"
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
          var d;
          d = $.Deferred();
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
