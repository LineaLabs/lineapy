Pipeline Writing (Breaking Down the Graph)
------------------------------------------

Overview
~~~~~~~~

A diagram to show the main abstractions we use to break down a graph as defined when users define a pipelines.

.. image:: ../../_static/images/graph_reader_classes.png
  :width: 600

The following sections will describe each abstraction in more detail.

Artifact Collection
~~~~~~~~~~~~~~~~~~~
The Artifact Collection is the main entrypoint and abstraction for defining the inputs and outputs modules and pipelines.
    
The ArtifactCollection can be thought of as a group of artifacts that the user selects and their corresponding graph(s) that will get refactored into reusable components.

The artifacts and variables can come from different user sessions, so the main job of ArtifactCollection is to group the inputs and outputs by session, creating a SessionArtifacts object for each session, and handling inter session dependencies.  

Session Artifacts
~~~~~~~~~~~~~~~~~
The Session Artifacts object is an abstraction for a workflow (subgraph of the LineaGraph) for one Session. 
Within this one Session, Session Artifacts defines the input artifacts and variables and the nodes needed to produce the output artifact.

Right now Session Artifacts does four major jobs:

1. Retrieve all Artifacts. Reuse precomputed "input" artifacts are searched up by their name and if a version is matched to this Session, it will be used as such.
2. Update Node Context, most importantly which nodes have dependencies on each other. Right now, this roughly performs the job of the MutationTracker and is important for the next step.
3. Slice Session Artifacts, breaking down the Session Artifacts subgraph into further smaller non-overlapping components called NodeCollections.
4. Determine dependencies between the finalized NodeCollections breakdown.

NodeCollections
~~~~~~~~~~~~~~~

Node Collections are the small non-overlapping subgraphs that are created when "refactoring" all the user code in a Session Artifacts.
There are a few main types of Node Collections.

- ImportNodeCollection, contains all nodes that handle imports in a Session.
- InputVarNodeCollection, a set of nodes which define the input variables for a NodeCollection.
- UserCodeNodeCollection, a generic Node Collection which can produce some output variables. Usually these variables are common variables that are used in the computation of multiple artifacts and are thus targeted to be "factored out" by the NodeCollection creating logic.
- ArtifactNodeCollection, a special type of UserCodeNodeCollection where the output is an artifact. This NodeCollection comes in two types depending on if the output of this NodeCollection is an artifact the user specified as an output or reuse_precomputed originally.
