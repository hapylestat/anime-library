
var opt = {
  general:{
    mal_anime_url:'http://myanimelist.net/anime/',

    get_mal_anime_link:function(id){
      return this.mal_anime_url + id;
    }
  },

  api: {
    root_url:'api',
    get_image_url:'/?q=image&data=', // GET
    get_info_url:'/?q=info&data=', // GET
    get_list_url:'/?q=list', // GET
    get_image_bulk_url:'/?q=image_bulk', // POST
    get_bulk_info_url:'/?q=bulk_info', // POST

    //===public methods

    get_bulk_info:function(){
      return this.root_url + this.get_bulk_info_url;
    },
    get_list:function(){
      return this.root_url + this.get_list_url;
    },
    get_image:function(id){
      return this.root_url + this.get_image_url + escape(id);
    },
    get_bulk_image:function(){
      return this.root_url + this.get_image_bulk_url;
    },
    get_info:function(name){
      // ToDo: should be here escaping?
      return this.root_url + this.get_info_url + name;
    }


  }

}
