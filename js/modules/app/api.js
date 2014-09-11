
var api = {
  loadURI:function(req, callback, options) {
    var options = options || {};

    //$.getJSON(req,function(data){
    //   callback(data, options);
    // });
    var jqxhr = $.getJSON(req ,function(data){
       callback(data, options);
     })
       .error(function(jqXHR){
          document.write(jqXHR.responseText);
       });

  },
  postURI:function(req, post_data, callback, options){
    var options = options || {};
    post_data = JSON.stringify(post_data);
    //$.getJSON(req, post_data, function(data){
    //  callback(data, options);
    //});
    $.ajax({
      type: "POST",
      url: req,
      data: post_data,
      contentType: "application/json; charset=utf-8",
      success: function(data){
        try {
          callback(JSON.parse(data), options);
        } catch (e) {
          document.write(e);
        //document.write(data);
        }
      },
      dataType: "text"
    });
  },

  loadAnimeList:function(callback){
    this.loadURI(opt.api.get_list(), callback);
  },

  loadAnimeItem:function(item_name, callback, options){
   this.loadURI(opt.api.get_info(item_name), callback, options);
  },
  loadAnimeItems:function(item_list, callback, options){
    this.postURI(opt.api.get_bulk_info(), item_list, callback, options);
  },
  get_image:function(id, url){
     if (url == "@cached@") {
        return opt.api.get_image(id);
     } else {
      return url;
     }
  }

}
