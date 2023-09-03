var stramble = $('.stramble .target');
var strambleText = stramble.text();

stramble.each(function(e, i){

    var length = i.innerText.length;

    var newDom = '';
    var transitionDelay = .03;

    newDom += '<span class="strambable">';
    for(let k = 0; k < length; k++)
    {
        newDom += '<span data-letter="' + i.innerText[k] + '" style="transition-delay: ' + transitionDelay * k + 's" class="letter">' + i.innerText[k] +'</span>';
    }
    newDom += '</span>';

    i.innerHTML = newDom;

});

