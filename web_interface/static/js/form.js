$(document).ready(function() {

	$('form').on('submit', function(event) {
		$('#result').text('').hide();
		$('#loadingDiv').show();
		$('#glamoriseTextarea').attr('disabled', 'disabled');		
		$('#glamoriseJsonConfig').attr('disabled', 'disabled');
		$('#nalirXmlConfig').attr('disabled', 'disabled');
		$('#submitButton').attr('disabled', 'disabled');		
		$.ajax({
			data : {
				nlq : $('#glamoriseTextarea').val(),
				type : $('#hiddenType').val(),
				glamoriseJsonConfig : $('#glamoriseJsonConfig').val(),
				nalirXmlConfig : $('#nalirXmlConfig').val()
			},
			type : 'GET',
			url : '/backend'
		})
		.done(function(data) {
			$('#loadingDiv').hide();
			$('#glamoriseTextarea').removeAttr('disabled');
			$('#glamoriseJsonConfig').removeAttr('disabled');
			$('#nalirXmlConfig').removeAttr('disabled');
			$('#submitButton').removeAttr('disabled');
			if (data) {
				$('#result').html(data).show();			
			}			
		});

		event.preventDefault();

	});

});