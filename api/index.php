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
preg_match("/^[\w\d\s\,\!\'\-]+/i",$_GET["data"],$data);

$command = (count($command) > 0)? $command[0]: "";
$data = (count($data) > 0)? $data[0]: "";

// ====main function



function command_list($data) {
  global $SOURCE_LIST;
  $alist=new AnimeList($SOURCE_LIST);
  send_response("ok", $alist->load());
}


function command_info($data){
  global $MAL_USER,$MAL_PASS;

  if (trim($data) == "" ) {
    send_response("fail", "empty query");
    return;
  }

  $mal = new MyAnimeList();

  if (! $mal->login($MAL_USER,$MAL_PASS, false)){
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




// == initial request handlers
function send_response($result, $data, $cache=""){
  global $command;
  echo json_encode(array(
     "query" => $command,
     "status" => $result,
     "data" => $data,
     "cache" => $cache
    ),JSON_PRETTY_PRINT);
}

switch ($command){
  case "list":
   command_list($data);
   break;
  case "info":
   command_info($data);
  break;
  default:
    send_response("fail","Unknown command");
    break;
}


?>
