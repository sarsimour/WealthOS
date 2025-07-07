
        (function ($) {
            $("#search-input1").fundsearchbox({
                cols: ["_id", "NAME", "CODE", "NAME"],
                width: "257px",
                url: 'https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?callback=?&m=10&t=700&IsNeedBaseInfo=0&IsNeedZTInfo=0&key=',
                    onSelectFund: function (e) {
                        window.open("//fundf10.eastmoney.com/ccmx_" + e.CODE + ".html");

                    }
                })
        })(jQuery);
        //LoadFundSelect("jjlist", "ccmx", "000001");
        //ChkSelectItem("jjlist", "000001");
        var params = { code: strbzdm, year: "", month: "", topnum: 10 }
        LoadStockPos(params);
        setInterval(function () {
            var today = new Date();
            if (today.getDay() > 0 && today.getDay() < 6) {
                if (document.getElementById("gpdmList") != null) {
                    if (today.getHours() >= 9 && today.getHours() < 12) {
                        LoadGpzd(document.getElementById("gpdmList").innerHTML);
                    }
                    else if (today.getHours() >= 13 && today.getHours() < 15) {
                        LoadGpzd(document.getElementById("gpdmList").innerHTML);
                    }
                }
            }
        }, 20000);
    