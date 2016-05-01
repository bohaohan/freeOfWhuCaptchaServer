;(function(){
window.dbg=0;
if(window.dbg){
    //window.baseUrl='http://localhost/testjoking/1/whujw/extension/';
    window.baseUrl='http://localhost/testjoking/1/whujw/extension/';
}else{
    //window.baseUrl='http://testjoking.sinaapp.com/whujw/extension/';
}
window.baseUrl = 'http://fc.ziqiang.studio/static/';
window.jquerySrc= baseUrl + 'js/jquery-2.0.3.min.js';
window.bootstrapCssSrc=window.baseUrl+'css/bootstrap.css';
window.templateJsSrc=window.baseUrl+'js/build/template.js';
if(window.dbg){
	window.styleCssSrc=window.baseUrl+'style.css?v='+Math.random();
}else{
	window.styleCssSrc=window.baseUrl+'style.css?v=1';
}
window.intervalTime=1000;
window.jwBases=['http://210.42.121.134/','http://210.42.121.241/'];
window.canFuckIcode=0;

;(function(){
    var originalSetInterval=window.setInterval;
    window.setInterval=function(fn,delay,runImmediately){
        if(runImmediately){
        	fn();
        }
        return originalSetInterval(fn,delay);
    }
})();

var main={

	init:function(){
        
        var sid=setInterval(function(){
        	if(typeof $!='undefined'&&typeof $(document).on!='undefined'){
        		clearInterval(sid);
                window.jwBase=main.getJwBase();
		        main.afterLoadLib();
        	}else{
        		main.loadJs(jquerySrc);
        	}
        },window.intervalTime,true);

		main.loadJs(window.templateJsSrc);
		main.loadCss(window.bootstrapCssSrc);

	},

    getJwBase:function(){
        for(var i in window.jwBases){
            if(location.href.indexOf(window.jwBases[i])!=-1){
                return window.jwBases[i];
            }
        }
        return false;
    },

	afterLoadLib:function(){

        main.fixJs();
        main.fixCss();
        main.cacheData();

        main.fuckIcode();

        main.autoLogin();
        main.fastLogin();
        main.removeDisabledButton();
        main.gpa();
        main.exam();
        main.ping();
        main.bindRefreshIcode();
        main.cancelTutionTips();
		
	},

    fuckIcode:function(){
        if(!window.canFuckIcode){
            return;
        }
        if(!$('#captcha-img').length){
            return;
        }
        var main=this,imgData=main.getBase64Image(document.getElementById('captcha-img')),undefined;
        $.ajax({
            url:window.baseUrl+'icode.php',
            type:'POST',
            data:{
                data:imgData
            },
            success:function(e){
                if(e){
                    $('input[name="xdvfb"]').val(e);
                }
            }
        });
    },

    getBase64Image:function(img){
        var canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;

        var ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0);

        var dataURL = canvas.toDataURL("image/png");

        return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
    },

    cancelTutionTips:function(){
        if($('body').html().indexOf('对不起，您已欠费，不具有选课资格，请及时缴纳学费')!=-1){
            closeAlert();
        }
    },

    ping:function(){
        if(location.href.indexOf('stu_jxpg_lsn_list')==-1&&
            location.href.indexOf('jxpg_enterEvalForm')==-1&&
            location.href.indexOf('jxpg_confirmEnterForm')==-1
        ){
            return;
        }

        main.autoFillPing();
        
        $('#searchBox form').append('<span class="bs pingot"><button id="pingBtn" class="btn btn-sm btn-success">一键评教</button></span>');

    },

    autoFillPing:function(){
        $('input[name^="1st_Ateacher_"][value="A"]').each(function(i){
            $(this).prop('checked',true);
        });
        $('input[name^="Blesson_"][value="A"]').each(function(){
            $(this).prop('checked',true);
        });
        var ass=['老师教得真好，下次还选。','这课讲得不虚啊','老师讲得太好了。','老师教得好啊！','世上只有老师好。'],
            as=ass[Math.floor(Math.random()*ass.length)],undefined;
        $('textarea[name="Copen_1"]').val(as);
        $('a:contains("课程评价")').closest('li').trigger('click');
        $('input[name="Submit2"]').css('display','none');
        $('input[name="Submit"][value="确认"]').trigger('click');
    },

    getLessonheadids:function(){
        return {
            done:function(cb){
                $.ajax({
                    url:window.jwBase+'servlet/Svlt_QueryStuLsn?action=normalLsn',
                    success:function(html){
                        var $lt=$(html).filter('.listTable'),ls=[];
                        $lt.find('tr').each(function(i){
                            if(!i){
                                return;
                            }
                            ls.push($.trim($(this).find('td').eq(0).text()));
                        });
                        cb(ls);
                    },
                    error:function(){
                        cb(false);
                    }
                });
            }
        }
    },

    getExamlists:function(ls,yt){
        return {
            doing:function(cb){

                var len=ls.length||0,ts=0,us=0,undefined;
                for(var i=0;i<len;i++){
                    if(yt.term=='下'){
                        yt.term='%CF%C2';
                    }else{
                        yt.term='%C9%CF';
                    }  
                    $.ajax({
                        url:window.jwBase+'common/query_exam_arrange.jsp',
                        data:'year='+yt.year+'&term='+yt.term+'&cat1=%BF%CE%CD%B7%BA%C5&keyword1='+ls[i]+'&cat2=%D1%A7%C9%FA%C4%EA%BC%B6&keyword2=&submit=%B2%E9%D1%AF',
                        type:'POST',
                        complete:function(){
                            ts++;
                            cb(ts,len);
                        },
                        success:function(html){
                            var $tr=$(html).filter('.listTable').find('.tr_BODY');
                            if($tr.length){
                                us++;
                                $('.listTable').append($tr[0].outerHTML);
                                $('.total_count span').html(us);
                            }
                        }
                    })
                }
            }
        }

    },

    exam:function(){
        if(location.href.indexOf('query_exam_arrange')==-1){
            return;
        }
        $('.test-search').after('<div class="bs ex-btn-ot"><button class="btn btn-success btn-sm" id="exBtn">一键查询</button></div>');
        $(document).on('click','#exBtn',function(){
            var self=$(this),
                year=$('select[name="year"] option:selected').val(),
                term=$('select[name="term"] option:selected').val(),
                yt={year:year,term:term},
                undefined;
            $('.tr_BODY').remove();
            $('.total_count span').html('0');
            self.html('查询中').prop('disabled',true);
            main.getLessonheadids().done(function(ls){
                if(!ls){
                    self.html('自动查询').prop('disabled',false);
                }
                main.getExamlists(ls,yt).doing(function(ts,len){
                    if(ts==len){
                        self.html('一键查询').prop('disabled',false);
                    }else{
                        self.html('查询中('+ts+'/'+len+')').prop('disabled',true);
                    }
                });
            });
        });
    },

    gpa:function(){
        if(location.href.indexOf('Svlt_QueryStuScore')==-1){
            return;
        }

        var ss=window.scores=main.getScores();

        $('.listTable tr:first').prepend('<th>选定</th>');
        $('.listTable tr:gt(0)').prepend('<td><input type="checkbox" class="scoreItemCb"/></td>');


        var scoreButtonsHtml=template('tpl/scoreButtons');
        $('.listTable').before(scoreButtonsHtml);
        $('.listTable').after(scoreButtonsHtml);

        for(var i in window.scores){
            if(window.scores[i].score>=60){
                $('.scoreItemCb').eq(i).prop('checked',true);
            }
        }
        main.calcGpa();


        $(document).on('click','.listTable tr',function(e){
            var self=$(this),
                undefined;
            if(e.target.className=='scoreItemCb'){
                return;
            }
            self.find('.scoreItemCb').prop('checked',function(i,v){
                return !v;
            });
            main.calcGpa();
        });      

        $(document).on('click','.scoreSelect',function(){
            var self=$(this),
                type=self.attr('data-type'),
                undefined;
            if(type=='all'){
                $('.scoreItemCb').prop('checked',true);
                main.calcGpa();
                return;
            }
            if(type=='reverse'){
                $('.scoreItemCb').prop('checked',function(i,v){
                    return !v;
                });
                main.calcGpa();
                return;
            }
            $('.listTable tr:contains('+type+')').find('.scoreItemCb').prop('checked',false);
            main.calcGpa();
        });

       
    },

    getScores:function(){
        var rs=[],
            dict={
                'lesson_headid':1,
                'lesson_name':2,
                'lesson_type':3,
                'credit':4,
                'teacher':5,
                'academy':6,
                'study_type':7,
                'year':8,
                'term':9,
                'score':10
            },
            hasCb=$('.scoreItemCb').length?true:false,
            undefined;

        $('.listTable tr').each(function(i){
            if(!i){
                return;
            }
            var self=$(this),undefined;
            rs[i-1]={};
            for(k in dict){
                rs[i-1][k]=main.string2Number($.trim(self.find('td').eq(hasCb?dict[k]:(dict[k]-1)).text()));
            }
        });
        return rs;
    },

    calcGpa:function(){
        var getGp=function(score){
            var gd=[
                [0,59,0],
                [60,63,1.0],
                [64,67,1.5],
                [68,71,2.0],
                [72,74,2.3],
                [75,77,2.7],
                [78,81,3.0],
                [82,84,3.3],
                [85,89,3.7],
                [90,100,4.0]
            ];
            for(var i in gd){
                if(score>=gd[i][0]&&score<=gd[i][1]){
                    return gd[i][2];
                }
            }
            return 0;
        },
        ss=window.scores?window.scores.slice():main.getScores(),
        gs={},gpa=0,totalCredits=0,avScore=0,totalScore=0,totalCreditGp=0,totalCreditScore=0,gp
        undefined;
        $('.scoreItemCb').each(function(i){
            var self=$(this),
                undefined;
            if(!self.prop('checked')){
                delete ss[i];
            }
        });

        for(var i in ss){
            totalCreditScore+=ss[i].score*ss[i].credit;
            gp=getGp(ss[i].score);
            totalCreditGp+=gp*ss[i].credit;
            totalCredits+=ss[i].credit;
        }
        avScore=totalCreditScore/totalCredits;
        gpa=totalCreditGp/totalCredits;
        if(!main.isNumeric(avScore)){
            avScore=0;
        }
        if(!main.isNumeric(gpa)){
            gpa=0;
        }
        if(!main.isNumeric(totalCredits)){
            totalCredits=0;
        }
        gs={
            av_score:avScore,
            gpa:gpa,
            total_credits:totalCredits
        };
        $('.tcBtn').html('已选学分：'+gs.total_credits.toFixed(1));
        $('.avBtn').html('加权平均分：'+gs.av_score.toFixed(3));
        $('.gpaBtn').html('绩点：'+gs.gpa.toFixed(3));
        return gs;
    },

    fixCss:function(){
      
        $('.inputWraper input').parent().addClass('bs');
        $('.inputWraper input').addClass('form-control');
    },
    
    fixJs:function(){
        $.browser={
            msie:0
        }
        $(document).on('DOMNodeInserted','#applyCouseT tr',function(){
            $(this).find('a[onclick="courseDel(this)"]').attr('href','javascript:;');
        });
    },

    autoLogin:function(){

        if(!window.canFuckIcode){
            return;
        }

        $(document).on('click','#fastLoginBtn,#loginBtn',function(){
            localStorage.is_auto_login='true';
        });

        $(document).on('click','a[href="/servlet/logout"]',function(){
            localStorage.is_auto_login='false';
        });


        if(localStorage.is_auto_login==='false'){
            return;
        }

        var lid=setInterval(function(){

            var $input=$('input[name="xdvfb"]');
            if($input.is(':focus')||$('input[name="qxftest"]').is(':focus')||$('input[name="pwd"]').is(':focus')){
                return;
            }

            if($input.val()&&$('input[name="qxftest"]').val()&&$('input[name="pwd"]').val()){
                clearInterval(lid);
                $('#fastLoginBtn').trigger('click');
            }

        },500,1);


    },

    fastLogin:function(){

        var main=this,undefined;
        $('.guest-tishi').after(template('tpl/fastLogin'));

        if(!window.$alp){
            $alp=$('#alertp').parent();
        }

        $(document).on('click','#fastLoginBtn',function(){
            var self=$(this),
                stuid=$('input[name="id"]').val(),
                password=$('input[name="pwd"]').val(),
                icode=$('input[name="xdvfb"]').val(),
                $alert=window.$alp,
                undefined;

            $('#alertp').html('');
            self.attr('disabled',true);

            var loginTimes=0;
            var isLogining=0;
            (function doLogin(){
                loginTimes++;
                isLogining=1;
                $.ajax({
                    url:window.jwBase+'servlet/Login',
                    data:{
                        id:stuid,
                        pwd:password,
                        xdvfb:icode
                    },
                    type:'POST',
                    success:function(html){
                        if(html.indexOf('验证码错误')!=-1){
                            $alert.html('验证码错误');
                            $('input[name="xdvfb"]').val('').focus();
                            main.refreshIcode();
                            self.removeAttr('disabled');
                            if(!window.canFuckIcode){
                                return;
                            }
                            var lid=setInterval(function(){
                                if($('input[name="xdvfb"]').val()==''){
                                    return;
                                }
                                if(icode==$('input[name="xdvfb"]').val()){
                                    return;
                                }
                                if(loginTimes<5){
                                    clearInterval(lid);
                                    $('#fastLoginBtn').trigger('click');
                                }
                            },500,1);
                        }else
                        if(html.indexOf('密码错误')!=-1){
                            $alert.html('学号或密码错误');
                            self.removeAttr('disabled');
                            isLogining=0;
                        }else
                        if(html.indexOf('数据库连接错误')!=-1){
                            if(isLogining){
                                $alert.html('数据库连接错误');
                                self.html('正在尝试第'+loginTimes+'次登录');
                                $('#stopFastLoginBtn').show();
                                doLogin();
                            }else{
                                 self.removeAttr('disabled').html('快捷登录');
                            }
                        }else
                        if(html.indexOf('<div id="login_info">')!=-1){
                            location.href=jwBase+'stu/stu_index.jsp';
                        }else{
                            console.log(html);
                        }
                        
                    },
                    error:function(e){
                        if(isLogining){
                            $alert.html('数据库连接错误');
                            self.html('正在尝试第'+loginTimes+'次登录');
                            $('#stopFastLoginBtn').show();
                            doLogin();
                        }else{
                             self.removeAttr('disabled').html('快捷登录');
                        }
                    }
                });
            })();

            $(document).on('click','#stopFastLoginBtn',function(){
                var self=$(this),
                    undefined;
                isLogining=0;
                self.css('display','none');
            });

            $(document).on('keydown','.inputWraper input',function(e){
                if(e.keyCode==13){
                    $('#fastLoginBtn').trigger('click');
                }
            });

        });

    },

    bindRefreshIcode:function(){

        $(document).on('click','#captcha-img',function(){
            main.refreshIcode();
        });

        $('#captcha-img').on('load',function(){
            main.fuckIcode();
        });

    },

    refreshIcode:function(){
        change();
    },

    removeDisabledButton:function(){
        $('input[value="选课"]').removeAttr('disabled');
    },

    cacheData:function(){

        $('input[name="id"]').val(main.getConfig('stuid'));
        $('input[name="pwd"]').val(main.getConfig('password'));

        $(document).on('change','input[name="id"]',function(){
            var self=$(this),
                undefined;
            main.setConfig('stuid',self.val());
        });

        $(document).on('change','input[name="pwd"]',function(){
            var self=$(this),
                undefined;
            main.setConfig('password',self.val());
        });

    },



    loadJs:function(src){
        var script=document.createElement('script'); 
        script.src=src;
        script.type='text/javascript'; 
        document.getElementsByTagName('head')[0].appendChild(script); 
    },

    loadCss:function(src){
        var link=document.createElement('link');
        link.rel='stylesheet';
        link.type='text/css';
        link.href=src;
        document.getElementsByTagName('head')[0].appendChild(link);
    },

    getConfig:function(key){
        if(!localStorage[key]){
            return '';
        }
        return localStorage[key];
    },

    setConfig:function(key,value){
        localStorage[key]=value;
    },

    fetchBlob:function(uri){

    	return {
    		done:function(cb){
				var xhr=new XMLHttpRequest();
				xhr.open('GET',uri,true);
				xhr.responseType='arraybuffer';

				xhr.onload=function(e){
					if(this.status==200){
						var blob=this.response;
						if(cb){
							cb(blob);
						}
					}
				};
				xhr.send();
    		}
    	}

    },

    blob2Base64:function(buffer){
	    var binary='';
	    var bytes=new Uint8Array(buffer);
	    var len=bytes.byteLength;
	    for(var i=0;i<len;i++) {
	        binary+=String.fromCharCode(bytes[i]);
	    }
	    return window.btoa(binary);
    },

    isNumeric:function(n){
      return !isNaN(parseFloat(n)) && isFinite(n);
    },

    string2Number:function(k){
        if(main.isNumeric(k)){
            return Number(k);
        }else{
            return k;
        }
    },

    inArray:function(stringToSearch,arrayToSearch){
        for(s=0;s<arrayToSearch.length;s++){
            thisEntry = arrayToSearch[s].toString();
            if(thisEntry == stringToSearch){
                return true;
            }
        }
        return false;
    }

}

main.init();

})();