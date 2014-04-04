<?php
if (!defined('ALIST')) { die('Working hard...'); }
/**
 * Anime item of Anime list representation
 */
class AnimeItem{
  // filters
  private $_dirs;
  private $_replace_mask = array(
                         array("/\_/"," "),
                         array("/\s\s/"," "),
                         array("/(^[A-Z][a-z\d]+)([A-Z])/","$1 $2"), //add space to sentence like SomeWord
                         array("/\s\-\s/"," "),
                         array("/\[[\d\w\s\-\.\+\&\~]+\]/",""),
                         array("/\([\d\w\s\-\.\+\&\~]+\)/",""),
                         array("/TV\+OVA/i",""),
                         array("/TV\+SPECIAL/i",""),
                         array("/\sTV\s*\-\s*\d/",""),
                         array("/\sTV\s*\d{1,3}/",""),
                         array("/\sTV/i",""),
                         array("/HWP/",""),
                         array("/OAV/",""),
                         array("/OVA/",""),
                         array("/HDRIP/i",""),
                         array("/\d{1,3}\~\d{1,3}/",""),
                         array("/\sHD/",""),
                         array("/\.\w{1,4}$/",""),
                         array("/\./"," "),
                         array("/\smovies/i","")
                        );
  private $_folder,$_filtered_folder,$_path;

  /**
   * normalize string format
   * @param  string $title
   * @return string
   */
  protected function normalize_title($title){
    foreach($this->_replace_mask as $mask){
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
    if ($this->_filtered_folder=="") $this->_filtered_folder=$this->normalize_title($this->_folder);
    return $this->_filtered_folder;
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
      $this->_dirs=func_get_args();
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
     return $list;
    }
}
?>
