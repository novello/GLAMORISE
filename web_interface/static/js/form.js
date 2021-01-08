$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				nlqs : $('#glamoriseTextarea').val()				
			},
			type : 'POST',
			url : '/backend_answer_nlqs'
		})
		.done(function(data) {

			if (data.pd) {
				$('#result').text(data.pd).show();				
			}			
		});

		event.preventDefault();

	});

});