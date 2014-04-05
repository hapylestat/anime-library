<html>
<head>
<title>Anime list</title>
  <link rel="stylesheet" href="css/vex.css"/>
  <link rel="stylesheet" href="css/vex-theme-default.css"/>
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js"></script>
  <script src="js/vex.combined.min.js"></script>
  <style type="text/css">
    .block
    {
        vertical-align: top;
        float:left;
    }
  </style>
</head>
<body>

<script>
vex.defaultOptions.className = 'vex-theme-default';

function showDialog(pic,name,folder,share,mal){
      vex.dialog.open({
      message: name,
      contentCSS:{ width: '800px' },
      input: " \
       <div> \
         <div class=\"block\">\
           <img id=\"apic\" src=\""+pic+"\"/>\
         </div>\
       <div class=\"block\">\
        <div>Title: <span>"+name+"</span> </div>\
        <div>Folder: <span style='font-size: 12px'>"+folder+"</span></div>\
        <div>Share: <span style='font-size: 12px'>"+share+"</span></div>\
        <div>MAL: <span><a href='" + mal +"' target='_blank'> goto </a></span></div>\
       </div>\
      </div>\
      ",
      buttons: [
         $.extend({}, vex.dialog.buttons.NO, {
          text: 'Close'
        })
      ],
    });
}
</script>
<?php
define('ALIST', 'nyaaa');
//define('DEVDEBUG', true);

include('config.php');
include('modules/ani_list.php');
include('modules/myanimelist.php');

$alist=new AnimeList($SOURCE_LIST);
// debug
if (isset($_GET["list"])){
  if ($_GET["list"] == "local"){
    $mylist=$alist->load();
    echo "<table>";
    foreach ($mylist as $item){
      echo "<tr><td>", $item,"</td><td>",$item->path(),"</td></tr>";
    }
    echo "</table>";
    die();
  }
}

$mylist=$alist->load();
//echo "<pre>",json_encode($mylist, JSON_PRETTY_PRINT),"</pre>";
//die();
$mal = new MyAnimeList();
if (! $mal->login($MAL_USER,$MAL_PASS, false)){
  die("MyAnimeList login failed ;(");
}

$cn=0;
$cb=0;
foreach ($mylist as $aitem){
    $r=$mal->search($aitem,  true);
    if (count($r) > 0) {
      echo "<a href='#' onclick='".sprintf("showDialog(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")",$r[0]->image,$aitem,$aitem->path(),$SHARE_MAP[$aitem->location()].'\\\\'.$aitem->folder(),"http://myanimelist.net/anime/".$r[0]->id)."'><img src='".$r[0]->image."' title='$aitem' width='225' height='309'/></a>";
     // echo "<pre>",json_encode($r[0], JSON_PRETTY_PRINT),"</pre>";
      $cn++;
    } else {
      echo "<b>$aitem</b>";
      $cb++;
    }

}

echo "<br/><br/><br/>Total: ", count($mylist), ", Found: ", $cn, ", Missed: " , $cb;
echo "<br/> Cache - ".$mal->stats();

?>
</body></html>
