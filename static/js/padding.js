// Modifica el header de acuerdo a al altura de la ventana
$(window).scroll(function() {
	var newWidth = $(window).width();
	if(newWidth > 992){
        if ($(this).scrollTop() > 1) {
            $('header').addClass("sticky");
            $("#formulario_header").addClass("pad12");
            $("#formulario_header").removeClass("pad18");
        } else {
            $('header').removeClass("sticky");
            $("#formulario_header").addClass("pad18");
            $("#formulario_header").removeClass("pad12");
        };
     }
});

// Los usa el boton de ayuda para mostrar la burbuja de ayuda rapida
function mostrarayudarapida() {
    var x = document.getElementById('id_burbuja_ayuda');
    x.style.display = 'block';
}
function ocultarayudarapida() {
    var x = document.getElementById('id_burbuja_ayuda');
    x.style.display= 'none';
}

//Controla el zoom y el ancho de la pantalla en la carga
$( document ).ready(function() {
    var newWidth = $(window).width();
    if (newWidth < 992) {
        if($("#sidebar").is(":visible")){
            $("#sidebar").hide();
            $("#resto").removeClass('col-xs-10');
            $("#resto").addClass('col-xs-12');
            $("#resto").removeClass('col-sm-10');
            $("#resto").addClass('col-sm-12');
            $("#resto").removeClass('col-md-10');
            $("#resto").addClass('col-md-12');
            $("#resto").removeClass('col-lg-10');
            $("#resto").addClass('col-lg-12');
        }
    }
});
