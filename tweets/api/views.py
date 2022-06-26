from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params


# class TweetViewSet(viewsets.GenericViewSet,
#                    viewsets.mixins.CreateModelMixin,
#                    viewsets.mixins.ListModelMixin):
class TweetViewSet(viewsets.GenericViewSet):
    """
        API endpoint that allows users to create, list tweets
        """
    queryset = Tweet.objects.all()
    # serializer_class = TweetCreateSerializer
    # serializer_class = TweetSerializer
    serializer_class = TweetSerializerForCreate


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]  # list page could be accessed by anyone even without login
        return [IsAuthenticated()]  # other pages require login

    @required_params(params=['user_id'])
    # def list(self, request, *args, **kwargs):
    def list(self, request):
        # """
        # 重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        # """
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)

        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        # 一般来说 json 格式的 response 默认都要用 hash (dict) 的格式
        # 而不能用 list 的格式（约定俗成）
        return Response({'tweets': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> 通过某个 query 参数 with_all_comments 来决定是否需要带上所有 comments
        # <HOMEWORK 2> 通过某个 query 参数 with_preview_comments 来决定是否需要带上前三条 comments
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    #  @action(permission=[...]) 或者用以上get_permissions
    def create(self, request):
        """
        重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        # save will trigger create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)

