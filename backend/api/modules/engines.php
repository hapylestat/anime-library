<?php
if (!defined('ALIST')) { die('Working hard...'); }


abstract class BaseEngine{
  private $mal_api = "http://myanimelist.net/api/";
  private $mal_account = "account/verify_credentials.xml";
  private $mal_search = "anime/search.xml?q=";



  // variables
  private $_user, $_pass;
  private $_req;
  private $_replace_mask ;
  private $_math_filterset;
  /**
   * Initialize base class
   */
  public function __construct(){
    $this->_replace_mask = masks::$search;
    $this->mal_account=$this->mal_api.$this->mal_account;
    $this->mal_search=$this->mal_api.$this->mal_search;
  }

  /*
   * Return stats from request
   */
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
   * @param  string  $mal api key
   * @param  boolean $check_login Check login or just cache tokens for the session
   * @return boolean
   */
  public function login($user, $pass, $api_key, $check_login=true){
    $this->_user=$user;
    $this->_pass=$pass;
    $this->_req = new cURLReq($api_key);
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

  function isXmlStructureValid($file) {
    $prev = libxml_use_internal_errors(true);
    $ret = true;
    try {
      new SimpleXMLElement($file, 0, false);
    } catch(Exception $e) {
      $ret = false;
    }
    if(count(libxml_get_errors()) > 0) {
      // There has been XML errors
      $ret = false;
    }
    // Tidy up.
    libxml_clear_errors();
    libxml_use_internal_errors($prev);
    return $ret;
  }

    /**
     * [basic] Looking for set of results on MAL
     * @param  string $name MAL Querry
     * @param  boolean $filter Filter search results to maximaze revalent output
     * @return string XML Parsed output
     */
  public function search($name, $filter=false){

  }

    /**
     * looking inside array for string
     * @param  array  $source Array to looking for in
     * @param  string  $search Search string
     * @param  integer $level_limit Apply to search number of pre-defined filters
     * @return boolean
     */
    private function _math_array(&$source,$search,$group=""){

    }

   /**
    * Check if gven title match to any title in several fields of MAL Item
    * @param  SimpleXMLNode $item single item from [search] function
    * @param  string $search Element to looking for
    * @param  int $level apply different level of filters if no positive result found
    * @return boolean
    */
  public function math_anime($item, $search,$group=""){}

}

?>
