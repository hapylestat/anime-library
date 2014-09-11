<?php
if (!defined('ALIST')) { die('Working hard...'); }

include_once("filters/masks.php");
/**
 * Anime item of Anime list representation
 */
class AnimeItem implements JsonSerializable{
  // filters
  private $_dirs;


  private $_folder,$_filtered_folder,$_path;

  /**
   * normalize string format
   * @param  string $title
   * @return string
   */
  protected function normalize_title($title){
    foreach(masks::$filter as $mask){
      $title = preg_replace($mask[0], $mask[1], $title);
    }
    return trim($title);
  }

  public function __construct($data,$opt=""){
   $this->_folder=$data;
   $this->_path=$opt;
  }

  public function folder(){
    return $this->_folder;
  }

  public function location(){
    return $this->_path;
  }

  public function path(){
    return $this->_path."/".$this->_folder;
  }

  public function __toString(){
    if ($this->_filtered_folder==""){
      $matches=array();
      if (preg_match(masks::$filter_custom, $this->_folder, $matches) === 1 && count($matches) > 1) {
        $this->_filtered_folder = $matches[1];
      } else {
       $this->_filtered_folder= $this->normalize_title($this->_folder);
      }
   }
    return $this->_filtered_folder;
  }

  public function jsonSerialize() {
        return array(
            "folder" => $this->_folder,
            "location" => $this->_path,
            "name" => $this->__toString()
          );
    }

}

/**
 * Anime list representation
 */
class AnimeList{
    private $_filter = array(
                  ".", "..", " ", ""
                  );
    /**
     * Create list of animes
     * @param string source1, source2, sourceN
     */
    public function __construct( /* arg list of sources*/ ){
      $args=func_get_args();
      if (count($args)==1){
        if (is_array($args[0])) $this->_dirs=$args[0];
      } else {
        $this->_dirs=$args;
      }
    }


    /**
     * Build anime list based on provided sources (with filtering of names)
     */
    public function load(){
      global $dirs;
      $list=array();
      // Generate summary array according to all sources
      foreach ($this->_dirs as $item){
        $content = scandir($item);
        array_walk($content,function (&$el,$key, $dir){
            $el=new AnimeItem($el, $dir);
           }, $item);
        $list=array_merge($list, $content);
      }

      // exclude filtered items
      $list = array_filter($list, function ($el){
                      return !in_array($el, $this->_filter);
                     });
     return array_values($list);
    }
}
?>
