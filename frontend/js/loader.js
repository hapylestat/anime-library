
var loader = {
  //---local variables
  _loaded:0,
  _toBeLoaded:0,
  _can_done:0,
  //----public methods
  loadFile:function(name, type){
    var head = document.getElementsByTagName('head')[0];
    var fref = null;
    switch (type){
      case "js":
        fref = document.createElement('script');
        fref.setAttribute('type', 'text/javascript');
        fref.setAttribute('src', 'js/modules/' + name + '.js');
        fref.onload = function(){
         setTimeout(function(){
          loader._loaded += 1;
          console.log('==> Name: ' + name + ".js");
          }, 50);
        }
        console.log('Name: ' + name + ".js");
        break;
      case "css":
        fref = document.createElement('link');
        fref.setAttribute('rel', 'stylesheet');
        fref.setAttribute('type', 'text/css');
        fref.setAttribute('href', 'css/' + name + '.css');
        console.log('Name: ' + name + ".css");
        fref.onload = function(){
          loader._loaded += 1;
          console.log('==> Name: ' + name + ".css");
        }
        break;
    }
    this._toBeLoaded += 1;
    head.appendChild(fref);
  },

  loadFiles:function(name_list, type, subdir){
    subdir = subdir || '';
    for (var item in name_list){
      this.loadFile(subdir + '/' + name_list[item], type);
    }
    this._can_done = 1;
  },

  loadJSONString:function(json){
    var data=JSON.parse(json);
    this.loadFiles(data.css.vendor, 'css', 'vendor');
    this.loadFiles(data.css.app, 'css', 'app');
    this.loadFiles(data.js.vendor, 'js', 'vendor');
    this.loadFiles(data.js.app, 'js', 'app');
    this.done();
  },

  loadJSONUri:function (path){
    this._can_done = 0;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open('GET', path, true);
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == "200") {
          loader.loadJSONString(xmlhttp.responseText);
        }
    };
    xmlhttp.send(null);
  },

  done:function(){
    if(this._can_done == 0) return; // do not execute if was used ajax request
    if (this._loaded >= this._toBeLoaded){
      this.onLoad();
    } else {
      setTimeout(function(){
       loader.done();
      }, 50);
    }
  },
  // ---------------- events
  onLoad:function(){}
}

window.onload= function(){
  loader.loadJSONUri('config.json');
  loader.done();
}


