$(document).ready(function() {
	var csrf_token = $('meta[name=csrf-token]').attr('content');
	$.ajaxSetup({
	    beforeSend: function(xhr, settings) {
	        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
	            xhr.setRequestHeader("X-CSRFToken", csrf_token);
	        }
	    }
	});

	
	$("button.vote").on("click", function() {
		var clicked_obj = $(this);
		var message_id = $(this).attr('data-id');
		var vote_type = $(this).attr('data-vote_type')

		$.ajax({
			url: '/vote',
			type: 'POST',
			data: JSON.stringify({ message_id: message_id, vote_type: vote_type}),
			contentType: "application/json; charset=utf-8",
        	dataType: "json",
			success: function(response){
				console.log(response);

				if(vote_type == "up") {
					clicked_obj.children()[0].innerHTML = " " + response.upvotes;
				} else {
					clicked_obj.children()[0].innerHTML = " " + response.downvotes;
				}
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
