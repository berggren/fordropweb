 var tl;
 function onLoad() {
 var eventSource = new Timeline.DefaultEventSource();
   var bandInfos = [
      Timeline.createBandInfo({
         eventSource:    eventSource,
         date:           date,
         width:          "85%", 
         intervalUnit:   Timeline.DateTime.HOUR, 
         intervalPixels: 100
     }),
     Timeline.createBandInfo({
     	 overview:       true,
         eventSource:    eventSource,
         date:           date,
         width:          "15%", 
         intervalUnit:   Timeline.DateTime.DAY, 
         intervalPixels: 200
     })
 
   ];
   bandInfos[1].syncWith = 0;
   bandInfos[1].highlight = true;
   tl = Timeline.create(document.getElementById("my-timeline"), bandInfos);
   Timeline.loadJSON(jsonurl, function(data, url) { eventSource.loadJSON(data, url); });
 }

 var resizeTimerID = null;
 function onResize() {
     if (resizeTimerID == null) {
         resizeTimerID = window.setTimeout(function() {
             resizeTimerID = null;
             tl.layout();
         }, 500);
     }
 }