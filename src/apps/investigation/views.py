from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from apps.investigation.models import Investigation
from apps.investigation.forms import TagForm
from apps.report.models import File
from apps.report.forms import UploadFileForm
import graphutils as gc
from utils import investigation_activity_stream
from uuid import uuid4
from django.template.defaultfilters import slugify

def get_people(investigation):
    """
    List of active people in a investigation, based on tags
    """
    people = [investigation.creator]
    tag_list = [x.name for x in investigation.tags.all()]
    files = File.objects.filter(tags__name__in=tag_list)
    for file in files:
        if file.user not in people:
            people.append(file.user)
    return people

@login_required
def create(request):
    """
    Create a new investigation
    """
    if request.method == 'POST':
        title = request.POST['title']
        if not title:
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        investigation, created = Investigation.objects.get_or_create(title=title, creator=request.user)
        if created:
            investigation.uuid = uuid4().urn
        investigation.investigator.add(request.user)
        investigation.save()
        # Add to neo4j
        gc.add_node(gc.neo4jdb, request, investigation, "investigation")
        gc.add_relationship(gc.neo4jdb, investigation.creator.get_profile().graph_id, investigation.graph_id, "created")
        return HttpResponseRedirect(investigation.get_absolute_url())


@login_required
def add_tag(request, id):
    investigation = Investigation.objects.get(pk=id)
    if request.user != investigation.creator:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    form = TagForm(request.POST, instance=investigation)
    if form.is_valid():
        obj = form.save(commit=False)
        for tag in form.cleaned_data['tags']:
            obj.tags.add(tag)
            #gc.add_node(gc.neo4jdb, request, tag, "investigation")
            #gc.add_relationship(gc.neo4jdb, investigation.creator.get_profile().graph_id, investigation.graph_id, "created")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def overview(request, id):
    """
    Dashboard of a investigation
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    upload_form = UploadFileForm()
    stream = investigation_activity_stream(investigation.id)
    tag_list = [x.name for x in investigation.tags.all()]
    files = File.objects.filter(tags__name__in=tag_list).distinct()
    return render_to_response('investigation/overview.html',
                                                                {
                                                                    'investigation': investigation,
                                                                    'uploadform': upload_form,
                                                                    'stream': stream,
                                                                    'people': people,
                                                                    'files': files,
                                                                    'tagform': TagForm(),
                                                                }, RequestContext(request))


@login_required
def timeline(request, id):
    """
    Timeline of investigation
    """
    investigation = Investigation.objects.get(pk=id)
    people = get_people(investigation)
    tag_list = [x.name for x in investigation.tags.all()]
    files = File.objects.filter(tags__name__in=tag_list).distinct()
    start_date = investigation.time_created.strftime('%a %b %d %Y %H:%M:%S')
    print start_date
    return render_to_response('investigation/timeline.html',
                                                                {
                                                                    'investigation': investigation,
                                                                    'startdate': start_date,
                                                                    'files': files,
                                                                    'people': people,
                                                                    'tagform': TagForm(),
                                                                }, RequestContext(request))


@login_required
def graph(request, id):
    """
    Visualization, objects in the graph with the investigation node as reference_node in neo4j
    Implemented with arbor.js, see the javascript in the template
    """
    investigation = Investigation.objects.get(pk=id)
    return render_to_response('investigation/graph.html',
                                                            {
                                                                'investigation': investigation
                                                            }, RequestContext(request))

@login_required
def related(request, id):
    investigation = Investigation.objects.get(id=id)
    ## Related from neo4j database. This needs work before enabled.
    #related = json.loads(gc.get_related(gc.neo4jdb, investigation.graph_id))['nodes']
    #people = []
    #investigations = []
    #files = []
    #for k,v  in related.items():
    #    if v['web_id']:
    #        if v['type'] == 'person':
    #            people.append(User.objects.get(pk=v['web_id']))
    #        if v['type'] == 'investigation':
    #            investigations.append(Investigation.objects.get(pk=v['web_id']))
    #        if v['type'] == 'report':
    #            files.append(File.objects.get(pk=v['web_id']))
    return render_to_response('investigation/related.html',
                                                            {
                                                                'investigation': investigation,
                                                            }, RequestContext(request))
