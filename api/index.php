<?php
define('ALIST', 'nyaaa');
//define('DEVDEBUG', true);

include_once('config.php');
include_once('modules/ani_list.php');
include_once('modules/engines/myanimelist.php');


// =========== Init script
class Arguments {
  private $_arglist=Array();
  private $_filtersets=Array(
       "word" => "/^[\w]+/",
       "ext" => "/^[\w\d\s\,\!\'\-\.\:\@\;\&\/]+/i"   // should we try here something better?
    );

  public function __construct($fields, $exclude_unknown = False){
    foreach ($_GET as $key => $value){
      if (array_key_exists($key,$fields)){
        preg_match($this->_filtersets[$fields[$key]],$value, $value);
        $value = (count($value) > 0)? $value[0]: "";
        if ($exclude_unknown) $this->_arglist = array_merge($this->_arglist, Array(strtolower($key) => $value));
      }
      if (! $exclude_unknown) $this->_arglist = array_merge($this->_arglist, Array(strtolower($key) => $value));
    }
  }

  public function post_data(){
    global $HTTP_RAW_POST_DATA;
    return $HTTP_RAW_POST_DATA;
  }

  public function __get($name){
    if (array_key_exists($name,$this->_arglist)) {
      return trim($this->_arglist[$name]);
    }
    return "";
  }
}

$arg=new Arguments(Array(
   "q" => "word",
   "data" => "ext"
  ), true);

// ====main function



function command_list($data) {
  global $SOURCE_LIST;
  $alist=new AnimeList($SOURCE_LIST);
  send_response("ok", $alist->load());
}


function command_info($data){
  global $MAL_USER,$MAL_PASS,$MAL_API_KEY;

  if (trim($data) == "" ) {
    send_response("fail", "empty query");
    return;
  }

  $mal = new MyAnimeList();

  if (! $mal->login($MAL_USER,$MAL_PASS,$MAL_API_KEY, false)){
   send_response("fail", "MyAnimeList login failed");
   return;
  }

  $r=$mal->search($data,  true);
    if (count($r) > 0) {
      send_response("ok", $r[0], $mal->stats());
    } else {
      send_response("fail", "search failed");
      return;
    }
}

function command_bulk_info($data){
  global $MAL_USER,$MAL_PASS,$MAL_API_KEY;
  $jdata='';

  try {
      $jdata = json_decode($data);
  } catch (Exception $e){
      send_response("fail", "search failed");
      return;
  }

  if (count($jdata) == 0) {
    send_response("fail", "empty query");
    return;
  }

  $mal = new MyAnimeList();

  if (! $mal->login($MAL_USER,$MAL_PASS,$MAL_API_KEY, false)){
   send_response("fail", "MyAnimeList login failed");
   return;
  }

  $jresponse= array();
  foreach ($jdata as $search_name){
      $r=$mal->search($search_name,  true);
        if (count($r) > 0) {
          array_push($jresponse, $r[0]);
        } else {
          array_push($jresponse, "");
        }
  }
  send_response("ok",$jresponse, $mal->stats());

}


function command_image($data){
  $req=new cURLReq();
  if ($req->cache_check_hit($data,typeImage)){
    header("Content-Type: image/jpeg");
    die($req->cache_get($data,typeImage));
  } else {
    global $MAL_USER,$MAL_PASS,$MAL_API_KEY;
    $mal = new MyAnimeList();
    if (! $mal->login($MAL_USER,$MAL_PASS,$MAL_API_KEY, false)){
     send_response("fail", "MyAnimeList login failed");
     return;
    }
    $r=$mal->search($data,  true);
    if (count($r) > 0) {
      if ($req->cache_check_hit($r[0]->title,typeImage)){
         header("Content-Type: image/jpeg");
         die($req->cache_get($r[0]->title,typeImage));
      } else {
        send_response("fail","Cache check after search failed ($data)");
      }
    } else {
      send_response("fail","Nothing found ($data)");
    }
  }
}

// == initial request handlers
function send_response($result, $data, $cache=""){
  global $arg;
  die(json_encode(array(
     "query" => $arg->q,
     "status" => $result,
     "data" => $data,
     "cache" => $cache
    ),JSON_PRETTY_PRINT));
}

switch ($arg->q){
  case "list":
    command_list($arg->data);
    break;
  case "bulk_info":
    command_bulk_info($arg->post_data());
    break;
  case "info":
    command_info($arg->data);
    break;
  case "image":
    command_image($arg->data);
    break;
  default:
    send_response("fail","Unknown command");
    break;
}


?>
