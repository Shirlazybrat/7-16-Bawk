$(document).ready(function(){
	$('.vote').click(function(e){
		e.preventDefault()
		var vid = $(this).attr('post-id')
		if ($(this).hasClass("vote-up")){
			//user clicked on the thumb up 
			var voteType = 1;
			console.log('up')
		}
		else {
			//user clicked on the thumb down
			var voteType = -1;
			console.log('down')
		}
		$.ajax({
			url: "/process_vote",
			type: "post",
			data: {vid:vid, voteType:voteType},
			success: function(result){
				console.log(result)
			},
			error: function(error){
				console.log("not working")
			}
		});
	});
});