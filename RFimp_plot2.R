install.packages('ggplot2')
install.packages('gcookbook')
library(ggplot2)
library(gcookbook)
testplot <- read.csv("C:/Users/DELL/Downloads/Compressed/data/2012imp.csv", header = T, stringsAsFactors = F)
head(testplot)
a <- ggplot(data=testplot)+geom_point(mapping=aes(x=X.IncMSE,y=reorder(variable,X.IncMSE),color=IncNodePurity,size=IncNodePurity))+ labs(title="2010",x="%IncMSE", y = "Variable name")+ theme_gray()
a + theme(panel.background=element_rect(fill='transparent', color='black'),
          legend.key=element_rect(fill='transparent', color='transparent'),
          axis.text=element_text(color='black'),
          panel.grid.major=element_line(colour='grey',size=0.5,linetype = "dotted"))