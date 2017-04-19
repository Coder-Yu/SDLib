![SDLib](http://i2.muimg.com/1949/a23f0509950f23f1.png)

SDLib: A Python library used to collect shilling detection methods. (for academic research)
<h2>How to Run it</h2>
<ul>
<li>1.Configure the **xx.conf** file in the directory named config. (xx is the name of the method you want to run)</li>
<li>2.Run the **main.py** in the project, and then input following the prompt.</li>
</ul>
<h2>How to Configure the Detection Method</h2>
<h3>Essential Options</h3>
<div>
 <table class="table table-hover table-bordered">
  <tr>
    <th width="12%" scope="col"> Entry</th>
    <th width="16%" class="conf" scope="col">Example</th>
    <th width="72%" class="conf" scope="col">Description</th>
  </tr>
  <tr>
    <td>ratings</td>
    <td>../dataset/averageattack/ratings.txt</td>
    <td>Set the path to the dirty recommendation dataset. Format: each row separated by empty, tab or comma symbol. </td>
  </tr>
 <tr>
    <td>label</td>
    <td>../dataset/averageattack/labels.txt</td>
    <td>Set the path to labels (for users). Format: each row separated by empty, tab or comma symbol. </td>
  </tr>
  <tr>
    <td scope="row">ratings.setup</td>
    <td>-columns 0 1 2</td>
    <td>-columns: (user, item, rating) columns of rating data are used;
      -header: to skip the first head line when reading data<br>
    </td>
  </tr>

  <tr>
    <td scope="row">MethodName</td>
    <td>DegreeSAD/PCASelect/etc.</td>
    <td>The name of the detection method<br>
    </td>
  </tr>
  <tr>
    <td scope="row">evaluation.setup</td>
    <td>-testSet ../dataset/testset.txt</td>
    <td>Main option: -testSet, -ap, -cv <br>
      -testSet path/to/test/file   (need to specify the test set manually)<br>
      -ap ratio   (ap means that the user set (including items and ratings) are automatically partitioned into training set and test set, the number is the ratio of test set. e.g. -ap 0.2)<br>
      -cv k   (-cv means cross validation, k is the number of the fold. e.g. -cv 5)<br>
     </td>
  </tr>

  <tr>
    <td scope="row">output.setup</td>
    <td>on -dir ./Results/</td>
    <td>Main option: whether to output recommendation results<br>
      -dir path: the directory path of output results.
       </td>
  </tr>
  </table>
</div>



<h2>How to extend it</h2>
<ul>
<li>1.Make your new algorithm generalize the proper base class.</li>
<li>2.Rewrite some of the following functions as needed.</li>
</ul>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- readConfiguration()<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- printAlgorConfig()<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- initModel()<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- buildModel()<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- saveModel()<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- loadModel()<br>
 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- predict()<br>
<h2>Implemented Methods</h2>

<div>
 <table class="table table-hover table-bordered">
  <tr>
		<th>Algorithm</th>
		<th>Paper</th>
  </tr>

  <tr>
	<td scope="row">DegreeSAD</td>
    <td>李文涛，等，一种基于流行度分类特征的托攻击检测算法， 自动化学报<br></td>
  </tr>

  </table>
</div>

<h2>How to generate spammers</h2>
<ul>
<li>1.Configure the **xx.conf** file in shillingmodels/config/. </li>
<li>2.Modify /shillingmodels/generateData.py as needed and run it.</li>
</ul>

<h2>How to Configure the Shilling Models</h2>
<h3>Essential Options</h3>
<div>
 <table class="table table-hover table-bordered">
  <tr>
    <th width="12%" scope="col"> Entry</th>
    <th width="16%" class="conf" scope="col">Example</th>
    <th width="72%" class="conf" scope="col">Description</th>
  </tr>
  <tr>
    <td>attackSize</td>
    <td>0.01</td>
    <td>The ratio of the injected spammers to genuine users</td>
  </tr>
 <tr>
    <td>fillerSize</td>
    <td>0.01</td>
    <td>The ratio of the filler items to all items </td>
  </tr>

  <tr>
    <td scope="row">MethodName</td>
    <td>DegreeSAD/PCASelect/etc.</td>
    <td>The name of the detection method<br>
    </td>
  </tr>
  <tr>
    <td scope="row">evaluation.setup</td>
    <td>-testSet ../dataset/testset.txt</td>
    <td>Main option: -testSet, -ap, -cv <br>
      -testSet path/to/test/file   (need to specify the test set manually)<br>
      -ap ratio   (ap means that the user set (including items and ratings) are automatically partitioned into training set and test set, the number is the ratio of test set. e.g. -ap 0.2)<br>
      -cv k   (-cv means cross validation, k is the number of the fold. e.g. -cv 5)<br>
     </td>
  </tr>

  <tr>
    <td scope="row">output.setup</td>
    <td>on -dir ./Results/</td>
    <td>Main option: whether to output recommendation results<br>
      -dir path: the directory path of output results.
       </td>
  </tr>
  </table>
</div>