<?php
if (!defined('ALIST')) { die('Working hard...'); }

include("curl_helper.php");

/**
 * Wrapper, which allows to work with MAL API
 */
class MyAnimeList{
  // api paths - http://myanimelist.net/modules.php?go=api
  private $mal_api = "http://myanimelist.net/api/";
  private $mal_account = "account/verify_credentials.xml";
  private $mal_search = "anime/search.xml?q=";

  // filters
  private $_replace_mask = array(
                             // mask | replace | filter group | apply changes
                             array("/\s\(tv\)/i","","soft",true),
                             array("/†/"," ","soft",true),
                             array("/\.$/","","soft",true),
                             array("/\sova$/","","soft",true),
                             array("/\soad$/","","soft",true),
                             array("/\,/","","soft",true),
                             array("/\?/","","soft",true),
                             array("/\;/"," ","soft",true),
                             array("/\:/","","soft",false),
                             array("/\!/","","soft",false),
                             array("/\?/","","soft",false),
                             array("/\-/","","soft",false),
                             array("/\-/"," ","soft",false),
                             array("/\./","","soft",false),
                             array("/\:/"," ","soft",false),
                             array("/\s[\d\w\!]+$/i","","soft",false),
                             array("/\//"," ","soft",false),
                             array("/[\d\s]*\:\s.*$/i","","soft", false),  // some title: absolute long
                             array("/\:\s/","-","soft",false),
                             array("/\![^\!]+/","!","hard",false),  // Cool man! some text => Cool man!
                             array("/the\sanimation/","","hard",false),
                             array("/\s.*$/i","","hard",false),
                             array("/(.*)\:(.*)\s\-(.*)/","$1$2$3","","hard",false), // saint seiya: the lost canvas - meiou shinwa
                             // =================   part 1: part2, cut part 1 and working with part 2
                             //array("/.*\:\s*/","","hard",false),
                             array("/(.*)\:\s*(.*)/","$2","soft",true),
                             array("/\s\-/","","soft",false)
                      );

  // variables
  private $_user, $_pass;
  private $_req;
  private $_math_filterset;
  /**
   * Initialize base class
   */
  public function __construct(){
    $this->_req = new cURLReq();
    $this->mal_account=$this->mal_api.$this->mal_account;
    $this->mal_search=$this->mal_api.$this->mal_search;
  }

  public function stats(){
    return $this->_req->get_stats();
  }

  /**
   * format title to normal one using filters
   * @param  string $title MAL anime title
   * @param  int $level Filter set to use
   * @return string formated title
   */
  protected function str_normalize($title, $level){
    $title = preg_replace($this->_replace_mask[$level][0], $this->_replace_mask[$level][1], $title);
    return trim($title);
  }

  /**
   * [basic] Authorization on MAL
   * @param  string  $user MAL Username
   * @param  string  $pass MAL Password
   * @param  boolean $check_login Check login or just cache tokens for the session
   * @return boolean
   */
  public function login($user, $pass, $check_login=true){
    $this->_user=$user;
    $this->_pass=$pass;
    if ($check_login) {
      $p=$this->_req->request($this->mal_account,$user,$pass);
      return ($this->_req->last_code() == 200);
    } else {
      return true; // when check login skipped, was returned fake result
    }
  }

   /**
    * Cut string while possible
    * @param  string $name String to cut
    * @return string       cuted string
    */
    private function try_search($name){
      $pos=strrpos($name," ");
      return ($pos!==false)?substr($name, 0, $pos):$name;
    }

    /**
     * Calculate count of possible cuts
     * @param string $name String to estimate
     * @return int estimated count number
     */
    private function try_count($name){
      return substr_count($name," ");
    }

    /**
     * [basic] Looking for set of results on MAL
     * @param  string $name MAL Querry
     * @param  boolean $filter Filter search results to maximaze revalent output
     * @return string XML Parsed output
     */
  public function search($name, $filter=false){
     // try to found result
     $p = $this->_req->request($this->mal_search.urlencode($name),$this->_user,$this->_pass,true,$name);

     // sigh, nothing found, try playing around to try us luck
     // if we found something, result will be stored to cache under initial query to safe time/traffic next time
     if ($this->_req->last_code() != 200) {
       $temp_name=$name;
       for ($round=0;$round<=$this->try_count($name);$round++){
        $temp_name=$this->try_search($temp_name);
        if (defined('DEVDEBUG')) echo "Try $round - $temp_name<br/>";

        // myanimelist api has an error, they is more strict to passed search string ;(
        if ($round == $this->try_count($name)-1){  //  there's left only one word
          $p = $this->_req->request($this->mal_search.urlencode($temp_name.":"),$this->_user,$this->_pass,false,$name);
          if ($this->_req->last_code() == 200 && strstr($p,$temp_name)!==FALSE) {
            $this->_req->put_cache_custom($name,$p);
            break;
          }
        }

        $p = $this->_req->request($this->mal_search.urlencode($temp_name),$this->_user,$this->_pass,true,$name);
        if ($this->_req->last_code() == 200) break; //  we found possible answer
       }
     }

      if ($this->_req->last_code() == 200) {

        $p=str_replace("&","&amp;",$p);
        if ($filter){ // math querry on all subset of results
          $list=simplexml_load_string($p)->entry;
          $result_list=array();

          #  step 1. Soft filter settings
          foreach ($list as $item){
           if ($this->math_anime($item,$name,"soft")) array_push($result_list, $item);
          }

          #  step 2. Harder filter settings, if step 1 fails
          if (count($result_list)==0) {
            foreach ($list as $item){
             if ($this->math_anime($item,$name)) array_push($result_list, $item);
            }
          }
          return $result_list;
        } else {
          return simplexml_load_string($p)->entry;
        }
      } else {
       return array();
      }
  }

    /**
     * looking inside array for string
     * @param  array  $source Array to looking for in
     * @param  string  $search Search string
     * @param  integer $level_limit Apply to search number of pre-defined filters
     * @return boolean
     */
    private function _math_array(&$source,$search,$group=""){
      $result=false;
      $this->_math_filterset=0;
      $max_level=count($this->_replace_mask);
      while (!$result && $this->_math_filterset<$max_level){
        $tmp=$source;
        if ($group=="" || $this->_replace_mask[$this->_math_filterset][2]=="$group"){
          array_walk($tmp, function(&$el){
                $el=$this->str_normalize($el,$this->_math_filterset);
              });
         }
        $result=in_array($search, $tmp);
        if ($this->_replace_mask[$this->_math_filterset][3]) $source=$tmp;
        if (defined('DEVDEBUG')) echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".$search."(filterset $this->_math_filterset) =>".implode(",",$tmp)."<br/>";
        $this->_math_filterset++;
      }
      return $result;
    }

   /**
    * Check if gven title match to any title in several fields of MAL Item
    * @param  SimpleXMLNode $item single item from [search] function
    * @param  string $search Element to looking for
    * @param  int $level apply different level of filters if no positive result found
    * @return boolean
    */
  public function math_anime($item, $search,$group=""){
    $search = strtolower($search);

    $items_base=array(strtolower($item->title), strtolower($item->english));
    $items=explode(';', strtolower($item->synonyms));

     $result=$this->_math_array($items_base,$search,$group);
     if (!$result) $result = $this->_math_array($items,$search,$group);

    return $result;
  }

}

?>
