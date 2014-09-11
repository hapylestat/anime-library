var SHARE_MAP={"/storage6/serials": "\\\\gate.home\\serials1",
               "/storage7/serials": "\\\\gate.home\\serials2"};

var OBJECTS_LOADED=0;
var OBJECTS_COUNT=0;

function show_plates(){
 $("#container_plates").toggleClass("hidden");
 $("#container_list").toggleClass("hidden");
}

function show_list(){
 $("#container_plates").toggleClass("hidden");
 $("#container_list").toggleClass("hidden");
}

function download_complete(storeid,data){
  localStorage.setItem(storeid, data);
}


function got_data(json, options){
  var options = options || {};
  var obj=json;

  if ( obj.query == "list" && obj.status == "ok") {
    var items = [];
    var opts = [];
    NProgress.start();
    OBJECTS_COUNT = obj.data.length;
    document.getElementById("status").innerHTML="Item count: " + obj.data.length.toString();
    for (var i=0;i<obj.data.length;i++){
      items.push(obj.data[i].name);
      opts.push({ name: obj.data[i].name, folder: obj.data[i].folder, location: obj.data[i].location});
      //api.loadAnimeItem(obj.data[i].name, got_data, { name: obj.data[i].name, folder: obj.data[i].folder, location: obj.data[i].location});
    }
    api.loadAnimeItems(items, got_data, opts);
  }
  if ( obj.query == "bulk_info" && obj.status =="ok") {
     for ( i=0; i < obj.data.length; i++){
       render.plate(obj.data[i], options[i]);
       OBJECTS_LOADED++;
       NProgress.inc();
     }
  }
  if ( obj.query == "info" && obj.status == "ok") {
     render.plate(obj.data, options);
     OBJECTS_LOADED++;
     NProgress.inc();
  }
  if ( obj.query == "info" && obj.status == "fail") {
    var item_name = options.name || '';
    document.getElementById("failed").innerHTML+=item_name +", "+obj.data+"<br/>";
    OBJECTS_LOADED++;
  }

  if (OBJECTS_LOADED >= OBJECTS_COUNT) {
    NProgress.done();
    $("#type-selector").toggleClass("hidden");
  }
}

function startApp(){
  OBJECTS_LOADED=0;
  OBJECTS_COUNT=0;
  $("#btn-plate").bind("click", function (){
     $(this).toggleClass("active");
     $("#btn-list").toggleClass("active");
     show_list();
  });
  $("#btn-list").bind("click", function (){
     $(this).toggleClass("active");
     $("#btn-plate").toggleClass("active");
     show_plates();
  });

  api.loadAnimeList(got_data);
}




loader.onLoad = function(){
  vex.defaultOptions.className = 'vex-theme-default';
  startApp();
}
