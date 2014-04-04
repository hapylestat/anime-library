<?php
define('ALIST', 'nyaaa');
//define('DEVDEBUG', true);

include('config.php');
include('modules/ani_list.php');
include('modules/myanimelist.php');

$alist=new AnimeList(
                     "/storage6/serials",
                     "/storage7/serials"
                     );
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
$mal = new MyAnimeList();
if (! $mal->login($MAL_USER,$MAL_PASS, false)){
  die("MyAnimeList login failed ;(");
}

$cn=0;
$cb=0;
foreach ($mylist as $aitem){
    $r=$mal->search($aitem,  true);
    if (count($r) > 0) {
      echo "<a href='http://myanimelist.net/anime/".$r[0]->id."'><img src='".$r[0]->image."' title='$aitem' width='225' height='309'/></a>";
      $cn++;
    } else {
      echo "<b>$aitem</b>";
      $cb++;
    }

}

echo "<br/><br/><br/>Total: ", count($mylist), ", Found: ", $cn, ", Missed: " , $cb;
echo "<br/> Cache - ".$mal->stats();

?>
