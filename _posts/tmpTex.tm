<TeXmacs|2.1.1>

<style|generic>

<\body>
  \<#666E\>\<#901A\>\<#5E74\>\<#91D1\>\<#73B0\>\<#503C\>\<#FF1A\>

  <\eqnarray*>
    <tformat|<table|<row|PV<rsub|0>|=|<frac|CF|1+r>+<frac|CF|<around*|(|1+r|)><rsup|2>>+<frac|CF|<around*|(|1+r|)><rsup|3>>+\<cdots\>+<frac|CF|<around*|(|1+r|)><rsup|n>>>|<row|<cell|>|<cell|=>|<cell|<frac|<frac|CF|1+r><around*|[|1-<around*|(|<frac|1|1+r>|)><rsup|n>|]>|1-<frac|1|1+r>>>>|<row|<cell|>|<cell|=>|<frac|CF<around*|[|1-<around*|(|<frac|1|1+r>|)><rsup|n>|]>|1+r-1>>|<row|<cell|>|<cell|=>|<cell|CF<frac|1|r><around*|[|1-<frac|1|<around*|(|1+r|)><rsup|n>><rsup|>|]>>>|<row|<cell|<text|>>|<cell|=>|<cell|CF
    <text|PVIFA<rsub|r,n>>>>>>
  </eqnarray*>

  \;

  FV<rsub|65> = 10000 * (1+5%)<rsup|20> * (1+8.5%)<rsup|40> = 693386.70

  <math|693386.70=PMT <frac|1|0.085><around*|[|1-<frac|1|<around*|(|1+0.085|)><rsup|20>>|]>>

  <math|PMT=73270.85>

  \;

  \<#6C38\>\<#7EED\>\<#5E74\>\<#91D1\>

  <\eqnarray*>
    <tformat|<table|<row|<cell|PV<rsub|0>>|<cell|=>|<cell|<frac|CF|1+r>+<frac|CF|<around*|(|1+r|)><rsup|2>>+>>>>
  </eqnarray*>

  \<#6295\>\<#8D44\>\<#7EC4\>\<#5408\>\<#7684\>\<#671F\>\<#671B\>\<#6536\>\<#76CA\>

  <math|E<around*|(|r|)>=w<rsub|1>E<around*|(|r<rsub|1>|)>+w<rsub|2>E<around*|(|r<rsub|2>|)>+\<ldots\>+w<rsub|n>E<around*|(|r<rsub|n>|)>>

  \<#6295\>\<#8D44\>\<#7EC4\>\<#5408\>\<#6536\>\<#76CA\>\<#7684\>\<#65B9\>\<#5DEE\>

  <\eqnarray*>
    <tformat|<table|<row|<cell|\<#3C3\><rsup|2>>|<cell|=>|E<around*|[|<around*|(|r-<wide|r|\<bar\>>|)><rsup|2>|]>>|<row|<cell|>|<cell|=>|<cell|E<around*|[|<around*|(|<below|<above|<big|sum>|n>|i=1>w<rsub|i>r<rsub|i>-<below|<above|<big|sum>|n>|i=1>w<rsub|i><wide|r|\<bar\>>|)><rsup|2>|]>>>|<row|<cell|>|<cell|=>|<cell|E<around*|[|<around*|(|<around*|(|<below|<above|<big|sum>|n>|i=1>w<rsub|i><around*|(|r<rsub|i>-<wide|r|\<bar\>>|)>|)><around*|(|<below|<above|<big|sum>|n>|j=1>w<rsub|j><around*|(|r<rsub|j>-<wide|r<rsub|j>|\<bar\>>|)>|)>|)><rsup|>|]>>>|<row|<cell|>|<cell|=>|<cell|E<around*|[|<around*|(|<below|<above|<big|sum>|n>|i,j=1>w<rsub|i>w<rsub|j><around*|(|r<rsub|i>-<wide|r<rsub|i>|\<bar\>>|)><around*|(|r<rsub|j>-<wide|r<rsub|j>|\<bar\>>|)>|)><rsup|>|]>>>|<row|<cell|>|<cell|=>|<cell|<below|<above|<big|sum>|n>|i,j=1>w<rsub|i>w<rsub|j>\<#3C3\><rsub|ij>>>>>
  </eqnarray*>

  \;

  L= <math|<frac|1|2>> <math|<big|sum><rsub|i=1><rsup|n>>
  <math|w<rsub|i>><math|w<rsub|j>><math|\<sigma\><rsub|i,j>> -
  <math|\<lambda\>>(<math|<big|sum><rsub|i=1><rsup|n>><math|w<rsub|i>><math|<wide|r<rsub|i>|\<bar\>>>
  - <math|<wide|r<text|>|\<bar\>>>)-<math|\<mu\>>(<math|<big|sum><rsub|i=1><rsup|n>><math|w<rsub|i>>
  -1<em|<strong|<verbatim|<samp|<verbatim|<strong|<em|>>>>>>>)

  \;

  \;

  \;

  \;

  \;

  \;

  \;

  \;

  \;

  \;

  \<#8D44\>\<#4EA7\>\<#7EC4\>\<#5408\>\<#5747\>\<#8861\>\<#72B6\>\<#6001\>\<#4E0B\>\<#FF1A\>

  <math|<big|sum><rsup|N><rsub|i=1>w<rsub|i>=0>

  <math|<big|sum><rsup|N><rsub|i=1>b<rsub|i,k>w<rsub|i>=0>
  (k\<#4E2A\>\<#5F0F\>\<#5B50\>)

  <math|<big|sum><rsup|N><rsub|i=1>w<rsub|i>E<around*|(|r<rsub|i>|)>=0>

  \<#6EE1\>\<#8DB3\>\<#4E0A\>\<#8FF0\>\<#5F0F\>\<#5B50\>\<#7684\>\<#6761\>\<#4EF6\>\<#4E0B\>\<#FF0C\>\<#63A8\>\<#5BFC\>\<#51FA\>

  <math|E<around*|(|r<rsub|i>|)>=\<#3BB\><rsub|0>+\<#3BB\><rsub|1>b<rsub|i,1>+\<#3BB\><rsub|2>b<rsub|i,2>+\<cdots\>+\<#3BB\><rsub|k>b<rsub|i,k>>
</body>

<\initial>
  <\collection>
    <associate|info-flag|none>
    <associate|page-medium|paper>
  </collection>
</initial>