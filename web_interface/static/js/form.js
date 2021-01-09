$(document).ready(function() {

	$('form').on('submit', function(event) {
		$('#result').text('').hide();
		$('#loadingDiv').show();
		$('#glamoriseTextarea').attr('disabled', 'disabled');
		$('#submitButton').attr('disabled', 'disabled');		
		$.ajax({
			data : {
				nlqs : $('#glamoriseTextarea').val()				
			},
			type : 'GET',
			url : '/backend_answer_nlqs'
		})
		.done(function(data) {
			$('#loadingDiv').hide();
			$('#glamoriseTextarea').removeAttr('disabled');
			$('#submitButton').removeAttr('disabled');
			if (data) {
				$('#result').html(data).show();			
			}			
		});

		event.preventDefault();

	});

});