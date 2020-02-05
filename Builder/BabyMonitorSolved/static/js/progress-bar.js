var i = 1;
$('.progress .circle').removeClass().addClass('circle');
$('.progress .bar').removeClass().addClass('bar');
setInterval(function() {
  $('.progress-course .circle:nth-of-type(' + i + ')').addClass('active');
  
  $('.progress-course .circle:nth-of-type(' + (i-1) + ')').removeClass('active').addClass('done');
  
  $('.progress-course .circle:nth-of-type(' + (i-1) + ') .label').html('&#10003;');
  
  $('.progress-course .bar:nth-of-type(' + (i-1) + ')').addClass('active');
  
  $('.progress-course .bar:nth-of-type(' + (i-2) + ')').removeClass('active').addClass('done');
  
  i++;
  
  if (i==0) {
    $('.progress .bar').removeClass().addClass('bar');
    $('.progress div.circle').removeClass().addClass('circle');
    i = 1;
  }
}, 1000);