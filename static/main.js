function log(msg, args) {
  console.log(msg, args);
}

function Company(data) {
  this.name = data['_id'];
}

function Crunchviz() {
  log('Crunchviz init');
}

Crunchviz.prototype.onDataLoad = function(data) {
  log('data loaded', data);
  this._companies = [];
  for (var i=0; i < data['stats'].length; i++) {
    var company = new Company(data['stats'][i]);
    this._companies.push(company);
  }
}

Crunchviz.prototype.getCompaniesload = function() {
  return this._companies;
}

Crunchviz.prototype.toHtml = function(company) {
  return '<p>' + company.name + '</p>';
}

Crunchviz.prototype.display = function() {
  var that = this;
  var _toHtml = function(idx, company) {
    console.log(this);
    var html = that.toHtml(company);
    $('#companies').append(html);
  }
  $.each(this._companies, _toHtml)
}

Crunchviz.prototype.load = function() {
  var that = this;
  $.ajax({
    dataType: 'jsonp',
    jsonp: 'jsonp',
    url: '/stats/?format=json',
    //success: this.onDataLoad(),
    success: function(data) {
      that.onDataLoad(data);
    },
  });
}

$(function() {
  var crunchviz = new Crunchviz();
  window.crunchviz = crunchviz;
  crunchviz.load();
});
