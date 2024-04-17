---
home: true
heroImage: /images/orange.jpg
---

<section class="quick-link">
<el-card class="basis" shadow="hover">
  <div slot="header">
    <span>basis</span>
  </div>
   <el-link href="/blog/basis/html/" type="info" :underline="false">html</el-link>
   <el-link href="/blog/basis/css/" type="info" :underline="false">css</el-link>
   <el-link href="/blog/basis/js" type="info" :underline="false">javascript</el-link>
</el-card>

<el-card class="frame" shadow="hover">
  <div slot="header">
    <span>framework</span>
  </div>
  <el-link href="/blog/framework/vue/" type="info" :underline="false">vue</el-link>
   <el-link href="/blog/framework/react/" type="info" :underline="false">react</el-link>
   <el-link href="/blog/framework/native-wx/" type="info" :underline="false">wx native</el-link>
   <el-link href="/blog/framework/electron/" type="info" :underline="false">electron</el-link>
</el-card>

<el-card class="others" shadow="hover">
  <div slot="header">
    <span>others</span>
  </div>
    <el-link href="/blog/others/ts/" type="info" :underline="false">typescript</el-link>
   <el-link href="/blog/others/node/" type="info" :underline="false">node</el-link>
   <el-link href="/blog/others/git/" type="info" :underline="false">git</el-link>
   <el-link href="/blog/others/algorithm/" type="info" :underline="false">algorithm</el-link>
   <el-link href="/blog/others/webpack/" type="info" :underline="false">vite / webpack</el-link>
   <!-- <el-link href="/blog/others/axios/" type="info" :underline="false">axios</el-link> -->
</el-card>
</section>

<el-divider></el-divider>
💡 想要成为优秀的前端工程师，需要**通过系统地学习和总结获取知识**，**通过练习获取编程能力**，**通过工作经验来获取架构和工程能力**。
<el-divider>🔚</el-divider>

<style>
.quick-link {
  display:flex;
  justify-content: space-between;
}

.el-card {
  width:30%
}

.el-card__header {
  padding:8px 0;
  text-align:center
}

.el-card__header span {
  font-size:24px;
  font-weight:500;
  background: linear-gradient(to right ,#63629c, #367cf5); 
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.el-card__body .el-link{
  margin-bottom:14px;
  text-align:center;
}

.el-link--inner {
background: linear-gradient(to top ,#e8dcfc, #5c5d9c); 
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.basis .el-link {
display:block;
width:100%
}

.frame .el-card__body,.others .el-card__body {
  display:flex;
  flex-wrap: wrap;
}

.frame .el-card__body .el-link,
.others .el-card__body .el-link{
  width:50%;
}

.el-link--inner {
 font-size:18px
}

</style>
