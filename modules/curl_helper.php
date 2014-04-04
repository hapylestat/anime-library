<?php
if (!defined('ALIST')) { die('Working hard...'); }
define('UPDATE_BIG_CACHE', false);
define('BIG_CACHE_SIZE', 15000);
/**
 * cURL helper
 */
class cURLReq{
   private $_http_code = 0;
   private $_mypath, $_cache;
   private $_c_hit=0;
   private $_c_miss=0;

   /**
    * Create instance of cURL helper
    */
   public function __construct(){
    $this->_mypath=realpath(dirname(__FILE__));
    $this->_cache=$this->_mypath."/../cache";
   }

  /**
   * Return last request http code
   * @return int
   */
  public function last_code(){
    return $this->_http_code;
  }

  public function get_stats(){
    return "Hit: ".$this->_c_hit." Miss: ". $this->_c_miss;
  }

  // simplest dummy cache
  /**
   * Return path to cache file based on given URL
   * @param  string $url Cache key
   * @return string cache file path
   */
  private function cache_get_path($url){
   return $this->_cache."/".sha1($url);
  }

  /**
   * Check present of cache file
   * @param  string $url Cache key
   * @return boolean
   */
  private function cache_check_hit($url){
    if (UPDATE_BIG_CACHE){
      $path=$this->cache_get_path($url);
        if (file_exists($path)){
          if (filesize($path) > BIG_CACHE_SIZE){
           unlink($path);
           return false;
        }
      }
    }
    return file_exists($this->cache_get_path($url));
  }

  /**
   * Return cached contend
   * @param  string $url Cache key
   * @return string
   */
  private function cache_get($url){
    return file_get_contents($this->cache_get_path($url));
  }

  /**
   * Store content to cache
   * @param  string $url Cache key
   * @param  string $content Content which need to be stored
   * @return int always 0
   */
  private function cache_put($url, $content){
    file_put_contents($this->cache_get_path($url), $content);
    return 0;
  }

  /**
   * Put to cache custom data (use it carefully)
   * @param string $key
   * @param string $content
   */
  public function put_cache_custom($key,$content){
    if (defined('DEVDEBUG')) echo "Cache: manually putting ". $key."<br/>";
    $this->cache_put($key,$content);
  }

  /**
   * Make request to remote host or service
   * @param  string  $url Request target
   * @param  string  $user HTTP Auth name
   * @param  string  $pass HTTP Auth password
   * @param  boolean $use_cache use build-in request cache, default no
   * @param  string  $custom_hash_base Custom hash base to store files
   * @return string Request response. Response code stored to last_code()
   */
  public function request($url,$user="",$pass="", $use_cache=false, $custom_hash_base=""){
    $page="";
    $hbase=($custom_hash_base=="")?$url:$custom_hash_base;

    if ($use_cache){
      if ($this->cache_check_hit($hbase)){
        if (defined('DEVDEBUG')) echo "<br>Cache:",$url,"<br>";
        $this->_http_code=200;
        $this->_c_hit++;
        return $this->cache_get($hbase);
      }
    }
    $this->_c_miss++;
    if (defined('DEVDEBUG')) echo "<br>",$url,"<br>";
    $s=curl_init();
    curl_setopt($s,CURLOPT_URL,$url);
    if ($user != "" && $pass !=""){
      curl_setopt($s,CURLOPT_USERPWD,"$user:$pass");
    }
    curl_setopt($s,CURLOPT_RETURNTRANSFER, true);

    $page=curl_exec($s);

    $this->_http_code=curl_getinfo($s,CURLINFO_HTTP_CODE);
    curl_close($s);

    if ($use_cache && $this->_http_code==200){
      $this->cache_put($hbase,$page);
    }
    return $page;
  }
}


?>
