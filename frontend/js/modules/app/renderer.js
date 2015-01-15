var render = {
  _dialog:null,

  add_cols:function(row, data){
    for (i=0;i<data.length;i++){
      var col=document.createElement("td");
      col.innerHTML=data[i];
      row.appendChild(col);
    }
    return;
  },
  plate: function(data, options){
     var item_folder = options.folder || '';
     var item_location = options.location || '';
    // var a=document.createElement("a");
     var img=document.createElement("img");
     var table=document.getElementById("container_list_table");
     var row=document.createElement("tr");


     //========plate style
     img.onclick=function(){
      //pic,name,folder,share,mal
      render.showDialog(api.get_image(data.title,data.image),data.title,item_location+"/"+item_folder,SHARE_MAP[item_location]+"\\"+item_folder,opt.general.get_mal_anime_link(data.id));
     }
     img.src=api.get_image(data.title,data.image);
     img.width=225;
     img.height=309;
     img.title=data.title;
     img.style.cursor="pointer";

      //===========style list
      img.style.cursor="pointer";
      this.add_cols(row,[
                  data.title,
                  "<a href='" + opt.general.get_mal_anime_link(data.id) + "' target='_blank'> goto </a>",
                  item_location+"/"+item_folder,
                  SHARE_MAP[item_location]+"\\"+item_folder
                  ]);

     document.getElementById("container_plates").appendChild(img);
     table.appendChild(row);
  },
  showDialog:function(pic,name,folder,share,mal){
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
        ]
      });
  }

}
