# import pandas as pd 
# from sentence_transformers import SentenceTransformer,datasets,losses,InputExample
# from sentence_transformers.evaluation import InformationRetrievalEvaluator,RerankingEvaluator
# print("ok")
# reviews=pd.read_csv("review_list")[["review","movie"]].iloc[:5]
# reviews=reviews[reviews["review"].notna()]
# reviews=reviews[reviews["review"].str.len()>0]
# train_data=list(map(lambda x: InputExample(texts=x),reviews.itertuples(index=False,name=None)))
# # corpus_data=list(map(lambda x: x,reviews.itertuples(index=False,name=None)))
# # print(corpus_data[:5])
# print("ok")
# model = SentenceTransformer("all-MiniLM-L6-v2")
# train_dataloader=datasets.NoDuplicatesDataLoader(train_data,batch_size=1)
# train_loss = losses.MultipleNegativesRankingLoss(model)
# num_epochs = 3
# warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)
# model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=num_epochs, warmup_steps=warmup_steps, show_progress_bar=True)
# model.save('/kaggle/working/lastest.pth')