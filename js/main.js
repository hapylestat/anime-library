var SHARE_MAP={"/storage6/serials": "\\\\gate.home\\serials1",
               "/storage7/serials": "\\\\gate.home\\serials2"};


function got_data(xmlhttp, options){
  var options = options || {};

  if (xmlhttp.readyState==4 && xmlhttp.status==200)
    {
      var obj=JSON.parse(xmlhttp.responseText);
      if ( obj.query == "list" && obj.status == "ok") {
        NProgress.start();
        document.getElementById("status").innerHTML="Item count: " + obj.data.length.toString();
        for (var i=0;i<obj.data.length;i++){
          //document.getElementById("myDiv").innerHTML+=obj.data[i].name + "<br>";
          loadXMLDoc("api/?q=info&data=" + obj.data[i].name, { folder: obj.data[i].folder, location: obj.data[i].location});
          NProgress.inc();
        }
        NProgress.done();
      }
      if ( obj.query == "info" && obj.status == "ok") {
         var item_folder = options.folder || '';
         var item_location = options.location || '';
         var a=document.createElement("a");
         var img=document.createElement("img");
         a.href="#";
         a.onclick=function(){
          //pic,name,folder,share,mal
          showDialog(obj.data.image,obj.data.title,item_location+"/"+item_folder,SHARE_MAP[item_location]+"\\"+item_folder,"http://myanimelist.net/anime/" + obj.data.id);
         }
         img.src=obj.data.image;
         img.width=225;
         img.height=309;
         img.title=obj.data.title;
         a.appendChild(img);
         document.getElementById("myDiv").appendChild(a);
         //document.getElementById("myDiv").innerHTML+="<img src='" + obj.data.image + "' width='225' height='309'/>";
      }
  } else {

  }
}

function loadXMLDoc(req, options)
{

var xmlhttp;
var options = options || {};
if (window.XMLHttpRequest)
  {// code for IE7+, Firefox, Chrome, Opera, Safari
  xmlhttp=new XMLHttpRequest();
  }
else
  {// code for IE6, IE5
  xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
xmlhttp.onreadystatechange=function(){got_data(xmlhttp, options);}
xmlhttp.open("GET",req,true);
xmlhttp.send();
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
  loadXMLDoc("api/?q=list");
}
