try:
    print " "
    print "=========== FrameRebuilder =========="

    try:
        groupNode = nuke.thisNode()
    except:
        groupNode = nuke.selectedNode()


    "Incorporate Reset Code from RichFrazer"
    n = nuke.thisNode()['inputframe']
    kt = nuke.thisNode()['kt']
    ko = nuke.thisNode()['ko']
    p = nuke.thisNode()['passthrough']
    n.clearAnimated()
    kt.clearAnimated()
    ko.clearAnimated()
    n.setAnimated()
    first_frame = nuke.thisNode().firstFrame()
    last_frame = nuke.thisNode().lastFrame() 
    n.animation(0).setKey(first_frame,first_frame)
    n.animation(0).setKey(last_frame,last_frame)
    p.setValue(0)

    n = nuke.thisNode()['inputframe']
    n.setAnimated()

    n.animation(0).setKey(first_frame,first_frame)
    n.animation(0).setKey(last_frame,last_frame)

    for i in xrange( first_frame, last_frame, 1 ):
        n.setValueAt(i, i)


    "Start Processing Groupnode Code"
    groupNode.begin()


    "Test if Kronos License is Active"
    try:
        k = nuke.nodes.Kronos()
        k["timing2"].setValue("Frame")
        kronos = True
    except:
        kronos = False

    if kronos == True:
        p = nuke.Panel("Choose mode")
        p.addEnumerationPulldown('Mode:', 'OFlow Kronos')
        result = p.show()
        mode = p.value("Mode:")
    else:
        mode = "OFlow"
        pass

    # for n in nuke.allNodes("OFlow2"):
    #     n["input.first"].setValue(f)
    #     n["input.last"].setValue(l)
    #     n["timingFrame2"].setExpression("parent.ko")
    #     n["vectorDetailLocal"].setExpression("parent.vector_detail")
    #     n["smoothnessLocal"].setExpression("parent.smoothness")
    #     n["resampleType"].setExpression("parent.resampling")
    #     n["flickerCompensation"].setExpression("parent.flicker_compensation")

    # kronos = False
    # for n in nuke.allNodes("Kronos"):
    #     try:
    #         n["input.first"].setValue(f)
    #         n["input.last"].setValue(l)
    #         n["timingFrame2"].setExpression("parent.ko")
    #         n["vectorDetailLocal"].setExpression("parent.vector_detail")
    #         n["smoothnessLocal"].setExpression("parent.smoothness")
    #         n["resampleType"].setExpression("parent.resampling")
    #         n["flickerCompensation"].setExpression("parent.flicker_compensation")
    #         kronos = True
    #     except Exception as e:
    #         kronos = False
    #         print e
    # groupNode.end()


    "Remove almost all nodes inside the group, Start with a clean Slate"
    for n in nuke.allNodes():
        if not "input" in n["name"].getValue().lower():
            if not "output" in n["name"].getValue().lower():
                nuke.delete(n)
    print "Deleted All nodes for Cleanup"


    "Get Nodes"
    inode = nuke.toNode("Input1")
    output = nuke.toNode("Output1")

    "Find Channels/Layers in Input"
    channels = inode.channels()
    layers = [c.split('.')[0] for c in channels]
    layers = list( set([c.split('.')[0] for c in channels]) )


    "Remove to add back to clean pipe"
    rm = nuke.nodes.Remove()
    rm.setInput(0,inode)


    "For each layer, let's shuffle it out, make our retime and oflow/kronos nodes and then put it back in a layered stream"
    count = 0
    #layers = ["all"]
    for l in layers:
        print "Creating Rebuild pipe for", l
        sh = nuke.nodes.Shuffle()
        sh.setInput(0,inode)
        sh["in"].setValue(l)
        sh["label"].setValue("\n\n")


        tw = nuke.nodes.TimeWarp()
        tw.setInput(0,sh)
        tw["lookup"].setExpression("parent.kt")

        
        if mode == "Kronos":
            n = nuke.nodes.Kronos()
            n.setInput(0,tw)
            n["input.first"].setValue(first_frame)
            n["input.last"].setValue(last_frame)
            n["retimedChannels"].setValue("rgba")
            n["timing2"].setValue("Frame")
            n["timingFrame2"].setExpression("parent.ko")
            n["vectorDetailLocal"].setExpression("parent.vector_detail")
            n["smoothnessLocal"].setExpression("parent.smoothness")
            n["resampleType"].setExpression("parent.resampling")
            n["flickerCompensation"].setExpression("parent.flicker_compensation")
            n["useGPUIfAvailable"].setExpression("parent.use_gpu")
        else:
            n = nuke.nodes.OFlow2()
            n.setInput(0,tw)
            n["input.first"].setValue(first_frame)
            n["input.last"].setValue(last_frame)
            n["retimedChannels"].setValue("rgba")
            n["timing2"].setValue("Frame")
            n["timingFrame2"].setExpression("parent.ko")
            n["vectorDetailLocal"].setExpression("parent.vector_detail")
            n["smoothnessLocal"].setExpression("parent.smoothness")
            n["resampleType"].setExpression("parent.resampling")
            n["flickerCompensation"].setExpression("parent.flicker_compensation")
            n["useGPUIfAvailable"].setExpression("parent.use_gpu")


        sh2 = nuke.nodes.Shuffle()
        sh2.setInput(0,n)
        sh2["out"].setValue(l)

        copy = nuke.nodes.Copy()
        if count == 0:
            copy.setInput(0,rm)
        else:
            copy.setInput(0,copy_connect)
        copy["channels"].setValue(l)
        copy.setInput(1,sh2)
        copy_connect = copy
        count = count+1
        #print copy["name"].getValue()
        

    pt = nuke.nodes.Switch()
    pt.setInput(1,copy)
    pt.setInput(0,inode)
    pt["which"].setExpression("parent.passthrough")


    output.setInput(0,pt)


    groupNode.end()
    groupNode["mode"].setValue("Using "+mode)

except Exception as e:
    groupNode["mode"].setValue("ERROR:\n"+str(e))
    print e
    pass

