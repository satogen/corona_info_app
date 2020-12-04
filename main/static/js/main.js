$(function(){
    var countElm = $('.count'),
    countSpeed = 1;
 
    countElm.each(function(){
        var self = $(this),
        countMax = Number(self.attr('data-num')),
        thisCount = Number(self.text()),
        countNext = 0,
        countTimer;
        function timer(){
            countTimer = setInterval(function(){
                for(var i=0;i<111;i++){
                    countNext = countNext + 1;
                    self.text(countNext);
     
                    if(countNext >= countMax){
                        clearInterval(countTimer);
                        break;
                    }
                 }
            },countSpeed);
        }
        timer();
    });
 
});