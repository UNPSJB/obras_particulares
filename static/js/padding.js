// When the window loads, note the scroll position
// and add and remove classes accordingly

$(window).scroll(function() {
	if ($(this).scrollTop() > 1) {
		$('header').addClass("sticky");
        $("#formulario_header").addClass("pad12");
        $("#formulario_header").removeClass("pad18");
	} else {
		$('header').removeClass("sticky");
		$("#formulario_header").addClass("pad18");
		$("#formulario_header").removeClass("pad12");
	};
});


// Make the Back To Top slide smoothly

