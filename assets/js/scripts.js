$(function(){

    let datatable_count = $("#datatables").length

    
    let proccess = {
        status : []
    }
    let _interval = []
    
    if(datatable_count>0){
        $('#datatables').DataTable();
    }


    /**
     * loading bar
     */
        let loading_bar = $("#datatables_ .loading_bar").length

        // console.log(loading_bar)

        if(loading_bar > 0){
            loadBar()
        }

        function loadBar()
        {
            $("#datatables_ .loading_bar").each(function(){
                let _thisEl = $(this)
                let init = _thisEl.attr('data')
                proccess.status[init] = false
                getTotalProgress(init,_thisEl,proccess)
                    _interval[init] = setInterval(function(){
                        if(proccess.status[init] === false){
                            getTotalProgress(init,_thisEl,proccess)
                        }else{
                            clearInterval(_interval[init]);
                        }
                    }, 10000);
            })
        }


        $(document).on("click",".start_stop",function(){
            let elm = $(this)
            let init = elm.attr('data')
            let value = elm.attr('data-value')
            let type = elm.attr('data-type')

            elm.html('Wait ...')
            elm.prop('disabled',true)

            $.ajax({
                // 'async': false,
                'type': "GET",
                // 'global': false,
                'dataType': 'json',
                'url': "./../administrator/start-stop",
                'data': { 
                    'init' : init,
                    'value' : value
                },
                'success': function (response) {
                    if(response.status === true){
                        if(type === 'acm'){
                            loadBar()
                        }
                        if(type === 'spring'){
                            loadBar()
                        }
                        if(type === 'ieee'){
                            loadBadgeBar()
                        }
                    }
                    elm.prop('disabled',false)
                }
            })
        })

        function getTotalProgress(init,elm, proccess)
        {
            $.ajax({
                // 'async': false,
                'type': "GET",
                // 'global': false,
                'dataType': 'json',
                'url': "./../administrator/scrapping/get-total-db",
                'data': { 
                    'init' : init,
                },
                'success': function (response) {
                    if(response.status === true){
                        _done = response.data.break
                        proccess.status[init] = _done
                        displayProccessHtml(response.data,elm)
                    }
                }
            })
        }

        function displayProccessHtml(data,elm)
        {
            elm.find('.progress-bar').css({"width": data.percent+'%'});
            elm.find('.progress-bar').html(data.percent+'% '+"( "+data.hasinsert.toLocaleString('en-US')+" / "+data.limit.toLocaleString('en-US')+" )");
            if(data.break === true){
                elm.parent().next().find('.start_stop').attr('data-value',0)
                elm.parent().next().find('.start_stop').removeClass('btn-danger').addClass('btn-primary')
                elm.parent().next().find('.start_stop').html('Start')
            }else{
                elm.parent().next().find('.start_stop').attr('data-value',1)
                elm.parent().next().find('.start_stop').removeClass('btn-primary').addClass('btn-danger')
                elm.parent().next().find('.start_stop').html('Pause')
            }
        }

    /**
     * badge_progress_bar
     */
        let badge_progress_bar = $("#datatables_ .badge_progress_bar").length


        if(badge_progress_bar>0){
            loadBadgeBar()
        }

        function loadBadgeBar()
        {
            $("#datatables_ .badge_progress_bar").each(function(){
                let _thisEl = $(this)
                let init = _thisEl.attr('data')
                proccess.status[init] = false
                getTotalBadgeProgress(init,_thisEl,proccess)
                    _interval[init] = setInterval(function(){
                        if(proccess.status[init] === false){
                            getTotalBadgeProgress(init,_thisEl,proccess)
                        }else{
                            clearInterval(_interval[init]);
                        }
                    }, 10000);
            })
        }

        
        function getTotalBadgeProgress(init,elm, proccess)
        {
            $.ajax({
                // 'async': false,
                'type': "GET",
                // 'global': false,
                'dataType': 'json',
                'url': "./../administrator/scrapping/get-total-db",
                'data': { 
                    'init' : init,
                },
                'success': function (response) {
                    if(response.status === true){
                        _done = response.data.break
                        proccess.status[init] = _done

                        elm.find('.number').html(response.data.hasinsert.toLocaleString('en-US'));
                        if(response.data.break === true){
                            elm.parent().next().find('.start_stop').attr('data-value',0)
                            elm.parent().next().find('.start_stop').removeClass('btn-danger').addClass('btn-primary')
                            elm.parent().next().find('.start_stop').html('Start')
                        }else{
                            elm.parent().next().find('.start_stop').attr('data-value',1)
                            elm.parent().next().find('.start_stop').removeClass('btn-primary').addClass('btn-danger')
                            elm.parent().next().find('.start_stop').html('Pause')
                        }
                    }
                }
            })
        }
    

});