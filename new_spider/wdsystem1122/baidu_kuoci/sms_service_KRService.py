#coding=utf-8
from ApiSDKJsonClient import *


class sms_service_KRService(ApiSDKJsonClient):

	def __init__(self):
		ApiSDKJsonClient.__init__(self, 'sms', 'service', 'KRService')

	def getEstimatedDataByBid(self, getEstimatedDataByBidRequest=None):
		return self.execute('getEstimatedDataByBid', getEstimatedDataByBidRequest)

	def getEstimatedData(self, getEstimatedDataRequest=None):
		return self.execute('getEstimatedData', getEstimatedDataRequest)

	def getKRFileIdByWords(self, getKRFileIdByWordsRequest=None):
		return self.execute('getKRFileIdByWords', getKRFileIdByWordsRequest)

	def getFilePath(self, getKRFileRequestParams=None):
		return self.execute('getFilePath', getKRFileRequestParams)

	def getFileStatus(self, getFileStatusRequest=None):
		return self.execute('getFileStatus', getFileStatusRequest)

	def getKRByQuery(self, getKRByQueryRequest=None):
		return self.execute('getKRByQuery', getKRByQueryRequest)

	def getKRCustom(self, getKRCustomRequest=None):
		return self.execute('getKRCustom', getKRCustomRequest)

	def getBidByWords(self, getBidByWordsRequest=None):
		return self.execute('getBidByWords', getBidByWordsRequest)



