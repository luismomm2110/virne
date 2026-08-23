graph [
  node_attrs_setting "_networkx_list_start"
  node_attrs_setting [
    name "cpu"
    type "resource"
    owner "node"
    distribution "uniform"
    dtype "int"
    generative "True"
    low "10"
    high "40"
  ]
  link_attrs_setting "_networkx_list_start"
  link_attrs_setting [
    name "bw"
    type "resource"
    owner "link"
    distribution "uniform"
    dtype "int"
    generative "True"
    low "20"
    high "80"
  ]
  topology___type "random"
  topology___random_prob "0.5"
  output___save_dir "dataset/v_nets"
  output___v_nets_save_dir "v_nets"
  output___v_nets_file_name "v_net.gml"
  output___events_file_name "events.yaml"
  output___setting_file_name "v_sim_setting.yaml"
  id 216
  arrival_time 4334.0
  lifetime 837.283205207771
  node [
    id 0
    label "0"
    cpu 21
  ]
  node [
    id 1
    label "1"
    cpu 30
  ]
  node [
    id 2
    label "2"
    cpu 21
  ]
  node [
    id 3
    label "3"
    cpu 12
  ]
  node [
    id 4
    label "4"
    cpu 36
  ]
  node [
    id 5
    label "5"
    cpu 14
  ]
  node [
    id 6
    label "6"
    cpu 24
  ]
  edge [
    source 0
    target 2
    bw 57
  ]
  edge [
    source 0
    target 4
    bw 44
  ]
  edge [
    source 0
    target 5
    bw 60
  ]
  edge [
    source 0
    target 6
    bw 77
  ]
  edge [
    source 1
    target 5
    bw 26
  ]
  edge [
    source 1
    target 6
    bw 64
  ]
  edge [
    source 2
    target 3
    bw 50
  ]
  edge [
    source 2
    target 4
    bw 78
  ]
  edge [
    source 2
    target 5
    bw 53
  ]
  edge [
    source 2
    target 6
    bw 21
  ]
  edge [
    source 3
    target 4
    bw 41
  ]
  edge [
    source 3
    target 5
    bw 45
  ]
  edge [
    source 3
    target 6
    bw 78
  ]
  edge [
    source 4
    target 6
    bw 66
  ]
  edge [
    source 5
    target 6
    bw 77
  ]
]
