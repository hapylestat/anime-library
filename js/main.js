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

function get_image(id, url){
 if (url == "@cached@") {
  return "api/?q=image&data=" + escape(id);
 } else {
  return url;
 }
}

function add_cols(row, data){
  for (i=0;i<data.length;i++){
    var col=document.createElement("td");
    col.innerHTML=data[i];
    row.appendChild(col);
  }
  return;
}

function got_data(json, options){
  var options = options || {};
  var obj=json;

  if ( obj.query == "list" && obj.status == "ok") {
    NProgress.start();
    OBJECTS_COUNT = obj.data.length;
    document.getElementById("status").innerHTML="Item count: " + obj.data.length.toString();
    for (var i=0;i<obj.data.length;i++){
      //document.getElementById("myDiv").innerHTML+=obj.data[i].name + "<br>";
      loadXMLDoc("api/?q=info&data=" + obj.data[i].name, { name: obj.data[i].name, folder: obj.data[i].folder, location: obj.data[i].location});
    }
  }
  if ( obj.query == "info" && obj.status == "ok") {
     var item_folder = options.folder || '';
     var item_location = options.location || '';
    // var a=document.createElement("a");
     var img=document.createElement("img");
     var table=document.getElementById("container_list_table");
     var row=document.createElement("tr");

     
     //========plate style
     img.onclick=function(){
      //pic,name,folder,share,mal
      showDialog(get_image(obj.data.title,obj.data.image),obj.data.title,item_location+"/"+item_folder,SHARE_MAP[item_location]+"\\"+item_folder,"http://myanimelist.net/anime/" + obj.data.id);
     }
     img.src=get_image(obj.data.title,obj.data.image);
     img.width=225;
     img.height=309;
     img.title=obj.data.title;
     img.style.cursor="pointer";

      //===========style list
      img.style.cursor="pointer";
      add_cols(row,[
                  obj.data.title,
                  "<a href='http://myanimelist.net/anime/" + obj.data.id + "' target='_blank'> goto </a>",
                  item_location+"/"+item_folder,
                  SHARE_MAP[item_location]+"\\"+item_folder
                  ]);

     document.getElementById("container_plates").appendChild(img);
     table.appendChild(row);
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

function loadXMLDoc(req, options)
{
  var options = options || {};

  $.getJSON(req,function(data){
     got_data(data, options);
   });
}



function showDialog(pic,name,folder,share,mal){
     vex.dialog.open({
      message: name,
      contentCSS:{ width: '800px' },
      input: " \
       <div> \
         <div class=\"block\">\
           <img id=\"apic\" src=\""+pic+"\"/>\
         </div>\
       <div class=\"block\">\
        <div>Title: <span>"+name+"</span> </div>\
        <div>Folder: <span style='font-size: 12px'>"+folder+"</span></div>\
        <div>Share: <span style='font-size: 12px'>"+share+"</span></div>\
        <div>MAL: <span><a href='" + mal +"' target='_blank'> goto </a></span></div>\
       </div>\
      </div>\
      ",
      buttons: [
         $.extend({}, vex.dialog.buttons.NO, {
          text: 'Close'
        })
      ],
    });
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

  loadXMLDoc("api/?q=list");
}
