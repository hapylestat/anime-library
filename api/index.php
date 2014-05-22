<?php
define('ALIST', 'nyaaa');
//define('DEVDEBUG', true);

include('../config.php');
include('../modules/ani_list.php');
include('../modules/myanimelist.php');



// =========== Init script
$command = array();
$data = array();

if (!isset($_GET["q"])) $_GET["q"] = "";
if (!isset($_GET["data"])) $_GET["data"] = "";

preg_match("/^[\w]+/",$_GET["q"],$command);
preg_match("/^[\w\d\s\,\!\'\-\.\:\@\;\&\/]+/i",$_GET["data"],$data);

$command = (count($command) > 0)? $command[0]: "";
$data = (count($data) > 0)? $data[0]: "";

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
        send_response("fail","Nothing found ($data)");
      }
    } else {
      send_response("fail","Nothing found ($data)");
    }
  }
}


// == initial request handlers
function send_response($result, $data, $cache=""){
  global $command;
  die(json_encode(array(
     "query" => $command,
     "status" => $result,
     "data" => $data,
     "cache" => $cache
    ),JSON_PRETTY_PRINT));
}

switch ($command){
  case "list":
   command_list($data);
   break;
  case "info":
   command_info($data);
  break;
   case "image":
   command_image($data);
  default:
    send_response("fail","Unknown command");
    break;
}


?>
