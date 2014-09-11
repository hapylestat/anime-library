<?php
if (!defined('ALIST')) { die('Working hard...'); }

class masks{
  // filters
    public static $search = array(
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


  public static $filter = array(
                           array("/\_/"," "),
                           array("/\s\s/"," "),
                           array("/(^[A-Z][a-z\d]+)([A-Z])/","$1 $2"), //add space to sentence like SomeWord
                           array("/\s\-\s/"," "),
                           array("/\[[^\[\]]+\]/",""), //old-\[[\d\w\s\-\.\+\&\~]+\]
                           array("/\([^\(\)]+\)/",""),//\([\d\w\s\-\.\+\&\~]+\)
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

  public static $filter_custom = "/\{([^\{\}]+)\}/";
}

?>
