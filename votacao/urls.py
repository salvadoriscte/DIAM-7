from django.urls import include,path
from django.contrib import admin
from django.urls import path
from .import views
app_name = 'votacao'
        # ex: votacao/
urlpatterns = [ path("", views.index, name='index'),
        # ex: votacao/1
        path("<int:questao_id>", views.detalhe, name='detalhe'),
        # ex: votacao/3/resultados
        path('<int:questao_id>/resultados', views.resultados,name = 'resultados'),
        # ex: votacao/5/voto
        path('<int:questao_id>/voto', views.voto, name='voto'),
        # ex: votacao/criarquestao
        path('criarquestao',views.criar_questao,name='criarquestao'),
        # ex: criaropcao
        path('<int:questao_id>/criaropcao', views.criar_opcao, name='criaropcao'),
        path('registo', views.registar_aluno, name='registo'),
        path('login', views.aluno_login, name='login'),
        path('logout', views.aluno_logout, name='logout'),
        path('perfil', views.perfil, name='perfil'),
        path('questao/<int:questao_id>/remover/', views.remover_questao, name='remover_questao'),
        path('questao/<int:questao_id>/opcao/<int:opcao_id>/remover/', views.remover_opcao, name='remover_opcao'),
            ]
