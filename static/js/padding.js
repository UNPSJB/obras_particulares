// When the window loads, note the scroll position
// and add and remove classes accordingly

$(window).scroll(function() {
	if ($(this).scrollTop() > 1) {
		$('header').addClass("sticky");
	} else {
		$('header').removeClass("sticky");
	};
});


// Make the Back To Top slide smoothly

