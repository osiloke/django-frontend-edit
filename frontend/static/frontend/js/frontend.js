$(function($) {    
    var loading = $('#editable-loading');
    loading.css({
        top: ($(window).height() - loading.height()) / 2 + $(window).scrollTop() + "px",
        left: ($(window).width() - loading.width()) / 2 + $(window).scrollLeft() + "px"

    }); 
    jQuery('.addable-form').each(function() {
       var form = this; 
       $("form#"+this.id).adminForm(
            {
                preSubmit:function(e,form) {
                    form.hide();
                    loading.show();
                    if (typeof tinyMCE != "undefined") {
                        tinyMCE.triggerSave();
                    }
                },
                resultParsed:function(e, params) {
                    if (params.status == true) {
                        location.reload();
                    } else {
                        loading.hide();
                        params.form.show();
                    }
                }
            }
        );
    });
    // Iterate through each of the addable areas and set them up.
    $.each($('.addable-link'), function(i ) {
        var link = $(this); 
        var expose = {color: "#333", loadSpeed: 200, opacity: 0.9};
        var overlay = {expose: expose, closeOnClick: true, close: ':button'};
        link.overlay(overlay);
    });
     $.each($('.addable-original-wrapper'), function(i ) {
        var wrapper = $(this);
        var link_holder = wrapper.find(".addable-link-holder");
        link_holder.css({
            top: 0,
            left: wrapper.width()
        });
    });
});