var T=Math.random();
var AFS_Protocol="http:";
if (document.location.protocol == "https:") AFS_Protocol="https:";
var Ref=document.referrer;
if (typeof(parent.document)!="unknown")
{
var F=parent.document.URL;
if (document.referrer==F) Ref=parent.document.referrer;
}
var S="usr="+AFS_Account+"P"+AFS_Tracker+"&js=1";
if (typeof AFS_Page == "undefined") var AFS_Page="unknown";
if (typeof AFS_Url == "undefined") var AFS_Url="unknown";
if (AFS_Page=="DetectName") {AFS_Page=document.title;}
if (AFS_Url=="DetectUrl") {AFS_Url=window.document.URL;}
S+="&title="+encodeURIComponent(AFS_Page);
S+="&url="+encodeURIComponent(AFS_Url);
S+="&refer="+encodeURIComponent(Ref);
S+="&rua=0";
if(typeof(screen)=="object")
{
S+="&resolution="+screen.width+"x"+screen.height;
S+="&color="+screen.colorDepth;
}
S+="&Tips="+T;
document.write("<a href=\"http://new.afsanalytics.com/?usr="+AFS_Account+"\" rel=\"nofollow\">");
document.write("<img border=0 src=\""+AFS_Protocol+"//"+AFS_Server+".afsanalytics.com/cgi-bin/connect.cgi?");
document.write(S);
document.write("\" border=0 alt=\"\" ></a>");
