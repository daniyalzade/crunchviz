function log(msg, args) {
  console.log(msg, args);
}

Number.prototype.formatMoney = function(c, d, t){
var n = this, c = isNaN(c = Math.abs(c)) ? 2 : c, d = d == undefined ? "," : d, t = t == undefined ? "." : t, s = n < 0 ? "-" : "", i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;
   return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
};

var fields = [
  ['name', 'name', 'Name', null, null],
  ['funding', 'funding', 'Funding', null, function(k) { return k.formatMoney(0, '.', ',');}],
  ['numEmployees', 'numEmployees', 'Number of Employees', null, null],
  ['category', 'category', 'Category', null, null],
  ['foundedAt', 'foundedAt', 'Founded At', function(k) { return new Date(1000 * k) }, null],
]

function _getId(name) {
  return name.replace(/[^0-9A-Za-z]/g, '')
}
function Company(data) {
  $.each(fields, (function(idx, field) {
    var exctractor = field[3] || function(k) { return k; }
    this[field[1]] = exctractor(data[field[0]]);
  }).bind(this));
}

Company.prototype.toHtml = function(company) {
  var html = "<tr id='%name'>".replace(/%name/, _getId(this.name))
  $.each(fields, (function(idx, field) {
    formatter = field[4] || function(k) { return k };
    html += '<td>' + formatter(this[field[1]]) + '</td>';
  }).bind(this));
  html += '</tr>';
  return html;
}

function Crunchviz() {
}

Crunchviz.prototype.onTagClick = function(event) {
  $(event.target).toggleClass('selected');
  this.filter();
}

Crunchviz.prototype.onColumnClick = function(event) {
  $(event.target).toggleClass('selected');
}

Crunchviz.prototype.addTags = function() {
  var tagCounts = {};
  $.each(this.getCompanies(), function(idx, company) {
    tagCounts[company.category] = (tagCounts[company.category] || 0) + 1;
  });
  for (var category in tagCounts) {
    var tag = "<a class='tag' href='#' rel='%count'>%name</a>"
      .replace(/%count/, tagCounts[category])
      .replace(/%name/, category);
    $('#tags').append(tag);
  }
  $.fn.tagcloud.defaults = {
    size: {start: 14, end: 24, unit: 'pt'},
  };
  $('#tags a').tagcloud();
  $('#tags').click(this.onTagClick.bind(this));
}
Crunchviz.prototype.onDataLoad = function(data) {
  this._companies = [];
  for (var i=0; i < data['stats'].length; i++) {
    var company = new Company(data['stats'][i]);
    this._companies.push(company);
  }
  var categoryAggs = {};
  $.each(this._companies) {
  }
  this.addTags();
}

Crunchviz.prototype.getCompanies = function() {
  return this._companies;
}

Crunchviz.prototype._getEmployeeFilter = function() {
  return (function(company) {
    return (company.numEmployees >= this.lowEmployee && company.numEmployees <= this.highEmployee);
  }).bind(this);
}

Crunchviz.prototype._getFundingFilter = function() {
  return (function(company) {
    console.log(company.funding, this.lowFunding, this.highFunding);
    return (company.funding >= this.lowFunding && company.funding <= this.highFunding);
  }).bind(this);
}

Crunchviz.prototype._getDateRangeFilter = function() {
  var lowYear = this.lowYear;
  var highYear = this.highYear;
  var dateRangeFilter = function(company) {
    var foundedYear = company.foundedAt.getFullYear();
    var val = (foundedYear >= lowYear && foundedYear <= highYear);
    return val;
  }
  return dateRangeFilter
}

Crunchviz.prototype._getTagFilter = function() {
  var selected = $.map($('.tag.selected'), function(elem) { return $(elem).text()});
  var tagFilter = function(company) {
    return $.inArray(company.category, selected) != -1;
  }
  return tagFilter;
}
Crunchviz.prototype._getFilters = function(dateRange) {
  return [
    this._getDateRangeFilter(),
    this._getTagFilter(),
    this._getEmployeeFilter(),
    this._getFundingFilter(),
    ]
}

Crunchviz.prototype.filter = function() {
  var filters = this._getFilters();
  var companies = this._companies;
  $.grep(companies, function(company, i) {
    var id = _getId(company.name);
    for (var idx=0; idx < filters.length; idx++) {
      if (!filters[idx](company)){
        $("#" + id).css('display', 'none');
        return false;
      }
    }
    $("#" + id).css('display', 'table-row');
    return true;
  })
}
Crunchviz.prototype.display = function() {
  var _toHtml = function(idx, company) {
    var html = company.toHtml();
    $('#companies table').append(html);
  }
  $('#companies').append('<table class="table table-bordered">');
  var thead = '<thead>';
  thead += '<tr>';
  $.each(fields, (function(idx, field) {
    thead += '<th>' + field[2] + '</th>';
  }).bind(this));
  thead += '</tr>';
  thead += '</thead>';
  var thead = $(thead)
  $('#companies table').append(thead);
  thead.click(this.onColumnClick.bind(this));
  $.each(this._companies, _toHtml)
  var table = $('#companies').append('</table>')
}

Crunchviz.prototype._selectRandomTags = function(numToSelect) {
  for (var i=0; i < numToSelect; i++) {
    var items = $('.tag').not('selected');
    $(items[Math.floor(Math.random()*items.length)]).toggleClass('selected');
  }
}

Crunchviz.prototype.load = function() {
  $.ajax({
    dataType: 'jsonp',
    jsonp: 'jsonp',
    url: '/stats/?format=json',
    //success: this.onDataLoad(),
    success: function(data) {
      this.onDataLoad(data);
      this.display();
      this._selectRandomTags(3);
      this.filter();
    }.bind(this),
  });
}

$(function() {
  var crunchviz = new Crunchviz();
  window.crunchviz = crunchviz;
  crunchviz.load();
});

$(function() {
  function _init_slider(min, max, selector, labelselector, name, formatter) {
    formatter = formatter || function(k) { return k };
    $(selector).slider({
      range: true,
      min: min,
      max: max,
      values: [ min, max ],
      slide: function( event, ui ) {
        $(labelselector).val(formatter(ui.values[0]) + " - " + formatter(ui.values[1]));
        crunchviz['low' + name] = ui.values[0];
        crunchviz['high' + name] = ui.values[1];
        crunchviz.filter();
      }
    });
    crunchviz['low' + name] = $(selector).slider( "values", 0 );
    crunchviz['high' + name] = $(selector).slider( "values", 1 );
    $(labelselector).val(formatter($(selector).slider("values",0)) +
        " - " + formatter($(selector).slider("values",1)));
  }

  _init_slider(1995, 2012, '#year-slider-range', '#year_range', 'Year')
  _init_slider(0, 1000, '#employee-slider-range', '#employee_range', 'Employee')
  _init_slider(0, Math.pow(10,8), '#funding-slider-range', '#funding_range',
      'Funding',
      function(k) { return k.formatMoney(0, '.', ','); }
      )
});
