
# Single QUA script generated at 2025-07-25 20:54:46.922657
# QUA library version: 1.2.1

from qm import CompilerOptionArguments
from qm.qua import *

with program() as prog:
    v1 = declare(int, )
    v2 = declare(fixed, )
    a1 = declare(fixed, size=25)
    a2 = declare(fixed, size=25)
    a3 = declare(fixed, size=10)
    atr_r4 = declare_stream(adc_trace=True)
    measure("readout", "rr6", atr_r4, demod.full("integW_cos", v2, ""), )
    save(v2, "full")
    reset_if_phase("rr6")
    measure("readout", "rr6", None, demod.sliced("integW_cos", a1, 8, ""), )
    with for_(v1,0,(v1<25),(v1+1)):
        r1 = declare_stream()
        save(a1[v1], r1)
    reset_if_phase("rr6")
    measure("readout", "rr6", None, demod.accumulated("integW_cos", a2, 8, ""), )
    with for_(v1,0,(v1<25),(v1+1)):
        r2 = declare_stream()
        save(a2[v1], r2)
    measure("readout", "rr6", None, demod.moving_window("integW_cos", a3, 25, 3, ""), )
    with for_(v1,0,(v1<25),(v1+1)):
        r3 = declare_stream()
        save(a3[v1], r3)
    with stream_processing():
        r1.save_all("demod_sliced")
        r2.save_all("demod_acc")
        r3.save_all("demod_mov")
        atr_r4.input1().save("raw_input")



####     SERIALIZATION WAS NOT COMPLETE     ####
#
#  Original   {  "script": {    "variables": [      {        "name": "v1",        "size": 1      },      {        "name": "v2",        "type": "REAL",        "size": 1      },      {        "name": "a1",        "type": "REAL",        "size": 25,        "dim": 1      },      {        "name": "a2",        "type": "REAL",        "size": 25,        "dim": 1      },      {        "name": "a3",        "type": "REAL",        "size": 10,        "dim": 1      }    ],    "body": {      "statements": [        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "streamAs": "atr_r0",            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "scalarProcess": {                        "variable": {                          "name": "v2",                          "loc": "stripped"                        }                      }                    }                  }                }              },              {}            ]          }        },        {          "save": {            "tag": "r1",            "source": {              "variable": {                "name": "v2",                "loc": "stripped"              }            },            "loc": "stripped"          }        },        {          "resetPhase": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            }          }        },        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "vectorProcess": {                        "array": {                          "name": "a1",                          "loc": "stripped"                        },                        "timeDivision": {                          "sliced": {                            "loc": "stripped",                            "samplesPerChunk": 8                          }                        }                      }                    }                  }                }              },              {}            ]          }        },        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "25",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "save": {                    "tag": "r2",                    "source": {                      "arrayCell": {                        "arrayVar": {                          "name": "a1",                          "loc": "stripped"                        },                        "index": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        },        {          "resetPhase": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            }          }        },        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "vectorProcess": {                        "array": {                          "name": "a2",                          "loc": "stripped"                        },                        "timeDivision": {                          "accumulated": {                            "loc": "stripped",                            "samplesPerChunk": 8                          }                        }                      }                    }                  }                }              },              {}            ]          }        },        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "25",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "save": {                    "tag": "r3",                    "source": {                      "arrayCell": {                        "arrayVar": {                          "name": "a2",                          "loc": "stripped"                        },                        "index": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        },        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "vectorProcess": {                        "array": {                          "name": "a3",                          "loc": "stripped"                        },                        "timeDivision": {                          "movingWindow": {                            "loc": "stripped",                            "samplesPerChunk": 25,                            "chunksPerWindow": 3                          }                        }                      }                    }                  }                }              },              {}            ]          }        },        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "25",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "save": {                    "tag": "r4",                    "source": {                      "arrayCell": {                        "arrayVar": {                          "name": "a3",                          "loc": "stripped"                        },                        "index": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        }      ]    }  },  "resultAnalysis": {    "model": [      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "raw_input"          },          {            "listValue": {              "values": [                {                  "stringValue": "@macro_adc_trace"                },                {                  "listValue": {                    "values": [                      {                        "stringValue": "@macro_input"                      },                      {                        "stringValue": "1"                      },                      {                        "listValue": {                          "values": [                            {                              "stringValue": "@re"                            },                            {                              "stringValue": "0"                            },                            {                              "stringValue": "atr_r0"                            }                          ]                        }                      }                    ]                  }                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "demod_acc"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r3"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "demod_mov"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r4"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "demod_sliced"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r2"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "full"          },          {            "stringValue": "auto"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r1"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "full_timestamps"          },          {            "stringValue": "auto"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "1"                },                {                  "stringValue": "r1"                }              ]            }          }        ]      }    ]  }}
#  Serialized {  "script": {    "variables": [      {        "name": "v1",        "size": 1      },      {        "name": "v2",        "type": "REAL",        "size": 1      },      {        "name": "a1",        "type": "REAL",        "size": 25,        "dim": 1      },      {        "name": "a2",        "type": "REAL",        "size": 25,        "dim": 1      },      {        "name": "a3",        "type": "REAL",        "size": 10,        "dim": 1      }    ],    "body": {      "statements": [        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "streamAs": "atr_r0",            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "scalarProcess": {                        "variable": {                          "name": "v2",                          "loc": "stripped"                        }                      }                    }                  }                }              }            ]          }        },        {          "save": {            "tag": "r1",            "source": {              "variable": {                "name": "v2",                "loc": "stripped"              }            },            "loc": "stripped"          }        },        {          "resetPhase": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            }          }        },        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "vectorProcess": {                        "array": {                          "name": "a1",                          "loc": "stripped"                        },                        "timeDivision": {                          "sliced": {                            "loc": "stripped",                            "samplesPerChunk": 8                          }                        }                      }                    }                  }                }              }            ]          }        },        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "25",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "save": {                    "tag": "r2",                    "source": {                      "arrayCell": {                        "arrayVar": {                          "name": "a1",                          "loc": "stripped"                        },                        "index": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        },        {          "resetPhase": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            }          }        },        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "vectorProcess": {                        "array": {                          "name": "a2",                          "loc": "stripped"                        },                        "timeDivision": {                          "accumulated": {                            "loc": "stripped",                            "samplesPerChunk": 8                          }                        }                      }                    }                  }                }              }            ]          }        },        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "25",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "save": {                    "tag": "r3",                    "source": {                      "arrayCell": {                        "arrayVar": {                          "name": "a2",                          "loc": "stripped"                        },                        "index": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        },        {          "measure": {            "loc": "stripped",            "qe": {              "loc": "stripped",              "name": "rr6"            },            "pulse": {              "loc": "stripped",              "name": "readout"            },            "measureProcesses": [              {                "analog": {                  "loc": "stripped",                  "demodIntegration": {                    "integration": {                      "loc": "stripped",                      "name": "integW_cos"                    },                    "target": {                      "loc": "stripped",                      "vectorProcess": {                        "array": {                          "name": "a3",                          "loc": "stripped"                        },                        "timeDivision": {                          "movingWindow": {                            "loc": "stripped",                            "samplesPerChunk": 25,                            "chunksPerWindow": 3                          }                        }                      }                    }                  }                }              }            ]          }        },        {          "for": {            "init": {              "statements": [                {                  "assign": {                    "expression": {                      "literal": {                        "value": "0",                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "condition": {              "binaryOperation": {                "op": "LT",                "left": {                  "variable": {                    "name": "v1",                    "loc": "stripped"                  }                },                "right": {                  "literal": {                    "value": "25",                    "loc": "stripped"                  }                },                "loc": "stripped"              }            },            "update": {              "statements": [                {                  "assign": {                    "expression": {                      "binaryOperation": {                        "left": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "right": {                          "literal": {                            "value": "1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "target": {                      "variable": {                        "name": "v1",                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "body": {              "statements": [                {                  "save": {                    "tag": "r4",                    "source": {                      "arrayCell": {                        "arrayVar": {                          "name": "a3",                          "loc": "stripped"                        },                        "index": {                          "variable": {                            "name": "v1",                            "loc": "stripped"                          }                        },                        "loc": "stripped"                      }                    },                    "loc": "stripped"                  }                }              ]            },            "loc": "stripped"          }        }      ]    }  },  "resultAnalysis": {    "model": [      {        "values": [          {            "stringValue": "save"          },          {            "stringValue": "raw_input"          },          {            "listValue": {              "values": [                {                  "stringValue": "@macro_adc_trace"                },                {                  "listValue": {                    "values": [                      {                        "stringValue": "@macro_input"                      },                      {                        "stringValue": "1"                      },                      {                        "listValue": {                          "values": [                            {                              "stringValue": "@re"                            },                            {                              "stringValue": "0"                            },                            {                              "stringValue": "atr_r0"                            }                          ]                        }                      }                    ]                  }                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "demod_acc"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r3"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "demod_mov"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r4"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "demod_sliced"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r2"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "full"          },          {            "stringValue": "auto"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "0"                },                {                  "stringValue": "r1"                }              ]            }          }        ]      },      {        "values": [          {            "stringValue": "saveAll"          },          {            "stringValue": "full_timestamps"          },          {            "stringValue": "auto"          },          {            "listValue": {              "values": [                {                  "stringValue": "@re"                },                {                  "stringValue": "1"                },                {                  "stringValue": "r1"                }              ]            }          }        ]      }    ]  }}
#
################################################

        
config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.03427316401433623,
                },
                "2": {
                    "offset": -0.004785346049418404,
                },
                "3": {
                    "offset": -0.027185835356852178,
                },
                "4": {
                    "offset": -0.007530590567993874,
                },
                "5": {
                    "offset": 0.0064196409297032665,
                },
                "6": {
                    "offset": 0.005306991551967946,
                },
                "7": {
                    "offset": -0.01004958944627166,
                },
                "8": {
                    "offset": 0.004911278856552271,
                },
                "9": {
                    "offset": 0.00821888106154563,
                },
                "10": {
                    "offset": 0.004321241386414653,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.20705431583788964,
                    "gain_db": 20,
                },
                "2": {
                    "offset": 0.24520065170098299,
                    "gain_db": 20,
                },
            },
        },
        "con2": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.022996400577754886,
                },
                "2": {
                    "offset": -0.03074378496929838,
                },
                "3": {
                    "offset": -0.009657680853590173,
                },
                "4": {
                    "offset": -0.02716331607469863,
                },
                "5": {
                    "offset": 0.0,
                },
                "6": {
                    "offset": 0.0,
                },
                "7": {
                    "offset": 0.009249489670579687,
                },
                "8": {
                    "offset": -0.0001508577334774491,
                },
                "9": {
                    "offset": -0.002423923022689978,
                },
                "10": {
                    "offset": -0.003703290379336752,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.20233268735851134,
                    "gain_db": 20,
                },
                "2": {
                    "offset": 0.193589471537298,
                    "gain_db": 20,
                },
            },
        },
        "con3": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": 0.0035796135749611665,
                },
                "2": {
                    "offset": -0.00040874841867035756,
                },
                "3": {
                    "offset": -0.0015584675683137685,
                },
                "4": {
                    "offset": 0.002931144598262927,
                },
                "5": {
                    "offset": -0.0002090710667964095,
                },
                "6": {
                    "offset": -0.0043554795748769115,
                },
                "7": {
                    "offset": -0.008383220770184413,
                },
                "8": {
                    "offset": -0.0019318483019448605,
                },
                "9": {
                    "offset": -0.01119244502107044,
                },
                "10": {
                    "offset": -0.007203587297926902,
                },
            },
            "digital_outputs": {},
            "analog_inputs": {
                "1": {
                    "offset": 0.2071748867439438,
                    "gain_db": 20,
                },
                "2": {
                    "offset": 0.23629523100002722,
                    "gain_db": 20,
                },
            },
        },
    },
    "pulses": {
        "zero": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "zero_wf",
            },
        },
        "const_pulse": {
            "operation": "control",
            "length": 100,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
        },
        "q1_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y360_Q_wf",
            },
        },
        "q1_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q1_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y180_Q_wf",
            },
        },
        "q1_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y90_Q_wf",
            },
        },
        "q1_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_mY90_Q_wf",
            },
        },
        "q1_ro_pulse": {
            "operation": "measurement",
            "length": 2400,
            "waveforms": {
                "I": "q1_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr1",
                "integW_sin": "integW_sin_rr1",
                "integW_minus_sin": "integW_minus_sin_rr1",
            },
            "digital_marker": "ON",
        },
        "q1_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_X180_I_wf",
                "Q": "q1_d_X180_Q_wf",
            },
        },
        "q1_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_X90_I_wf",
                "Q": "q1_d_X90_Q_wf",
            },
        },
        "q1_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_mX90_I_wf",
                "Q": "q1_d_mX90_Q_wf",
            },
        },
        "q1_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y180_I_wf",
                "Q": "q1_d_Y180_Q_wf",
            },
        },
        "q1_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y90_I_wf",
                "Q": "q1_d_Y90_Q_wf",
            },
        },
        "q1_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y360_I_wf",
                "Q": "q1_d_Y360_Q_wf",
            },
        },
        "q1_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_X360_I_wf",
                "Q": "q1_d_X360_Q_wf",
            },
        },
        "q1_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q1_d_mY90_I_wf",
                "Q": "q1_d_mY90_Q_wf",
            },
        },
        "q2_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y360_Q_wf",
            },
        },
        "q2_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q2_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y180_Q_wf",
            },
        },
        "q2_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y90_Q_wf",
            },
        },
        "q2_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_mY90_Q_wf",
            },
        },
        "q2_ro_pulse": {
            "operation": "measurement",
            "length": 2000,
            "waveforms": {
                "I": "q2_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr2",
                "integW_sin": "integW_sin_rr2",
                "integW_minus_sin": "integW_minus_sin_rr2",
            },
            "digital_marker": "ON",
        },
        "q2_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_X180_I_wf",
                "Q": "q2_d_X180_Q_wf",
            },
        },
        "q2_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_X90_I_wf",
                "Q": "q2_d_X90_Q_wf",
            },
        },
        "q2_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_mX90_I_wf",
                "Q": "q2_d_mX90_Q_wf",
            },
        },
        "q2_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y180_I_wf",
                "Q": "q2_d_Y180_Q_wf",
            },
        },
        "q2_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y90_I_wf",
                "Q": "q2_d_Y90_Q_wf",
            },
        },
        "q2_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y360_I_wf",
                "Q": "q2_d_Y360_Q_wf",
            },
        },
        "q2_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_X360_I_wf",
                "Q": "q2_d_X360_Q_wf",
            },
        },
        "q2_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q2_d_mY90_I_wf",
                "Q": "q2_d_mY90_Q_wf",
            },
        },
        "q3_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y360_Q_wf",
            },
        },
        "q3_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q3_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y180_Q_wf",
            },
        },
        "q3_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y90_Q_wf",
            },
        },
        "q3_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_mY90_Q_wf",
            },
        },
        "q3_ro_pulse": {
            "operation": "measurement",
            "length": 3600,
            "waveforms": {
                "I": "q3_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr3",
                "integW_sin": "integW_sin_rr3",
                "integW_minus_sin": "integW_minus_sin_rr3",
            },
            "digital_marker": "ON",
        },
        "q3_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_X180_I_wf",
                "Q": "q3_d_X180_Q_wf",
            },
        },
        "q3_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_X90_I_wf",
                "Q": "q3_d_X90_Q_wf",
            },
        },
        "q3_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_mX90_I_wf",
                "Q": "q3_d_mX90_Q_wf",
            },
        },
        "q3_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_Y180_I_wf",
                "Q": "q3_d_Y180_Q_wf",
            },
        },
        "q3_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_Y90_I_wf",
                "Q": "q3_d_Y90_Q_wf",
            },
        },
        "q3_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_Y360_I_wf",
                "Q": "q3_d_Y360_Q_wf",
            },
        },
        "q3_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_X360_I_wf",
                "Q": "q3_d_X360_Q_wf",
            },
        },
        "q3_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q3_d_mY90_I_wf",
                "Q": "q3_d_mY90_Q_wf",
            },
        },
        "q4_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y360_Q_wf",
            },
        },
        "q4_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q4_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y180_Q_wf",
            },
        },
        "q4_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y90_Q_wf",
            },
        },
        "q4_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_mY90_Q_wf",
            },
        },
        "q4_ro_pulse": {
            "operation": "measurement",
            "length": 3600,
            "waveforms": {
                "I": "q4_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr4",
                "integW_sin": "integW_sin_rr4",
                "integW_minus_sin": "integW_minus_sin_rr4",
            },
            "digital_marker": "ON",
        },
        "q4_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_X180_I_wf",
                "Q": "q4_d_X180_Q_wf",
            },
        },
        "q4_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_X90_I_wf",
                "Q": "q4_d_X90_Q_wf",
            },
        },
        "q4_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_mX90_I_wf",
                "Q": "q4_d_mX90_Q_wf",
            },
        },
        "q4_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_Y180_I_wf",
                "Q": "q4_d_Y180_Q_wf",
            },
        },
        "q4_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_Y90_I_wf",
                "Q": "q4_d_Y90_Q_wf",
            },
        },
        "q4_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_Y360_I_wf",
                "Q": "q4_d_Y360_Q_wf",
            },
        },
        "q4_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_X360_I_wf",
                "Q": "q4_d_X360_Q_wf",
            },
        },
        "q4_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q4_d_mY90_I_wf",
                "Q": "q4_d_mY90_Q_wf",
            },
        },
        "q5_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y360_Q_wf",
            },
        },
        "q5_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q5_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y180_Q_wf",
            },
        },
        "q5_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y90_Q_wf",
            },
        },
        "q5_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_mY90_Q_wf",
            },
        },
        "q5_ro_pulse": {
            "operation": "measurement",
            "length": 2800,
            "waveforms": {
                "I": "q5_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr5",
                "integW_sin": "integW_sin_rr5",
                "integW_minus_sin": "integW_minus_sin_rr5",
            },
            "digital_marker": "ON",
        },
        "q5_d_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_X180_I_wf",
                "Q": "q5_d_X180_Q_wf",
            },
        },
        "q5_d_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_X90_I_wf",
                "Q": "q5_d_X90_Q_wf",
            },
        },
        "q5_d_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_mX90_I_wf",
                "Q": "q5_d_mX90_Q_wf",
            },
        },
        "q5_d_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_Y180_I_wf",
                "Q": "q5_d_Y180_Q_wf",
            },
        },
        "q5_d_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_Y90_I_wf",
                "Q": "q5_d_Y90_Q_wf",
            },
        },
        "q5_d_Y360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_Y360_I_wf",
                "Q": "q5_d_Y360_Q_wf",
            },
        },
        "q5_d_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_X360_I_wf",
                "Q": "q5_d_X360_Q_wf",
            },
        },
        "q5_d_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q5_d_mY90_I_wf",
                "Q": "q5_d_mY90_Q_wf",
            },
        },
        "q6_grft": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_X180": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_X360": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_Y360": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y360_Q_wf",
            },
        },
        "q6_X90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_mX90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q6_Y180": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y180_Q_wf",
            },
        },
        "q6_Y90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y90_Q_wf",
            },
        },
        "q6_mY90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_mY90_Q_wf",
            },
        },
        "q6_ro_pulse": {
            "operation": "measurement",
            "length": 3200,
            "waveforms": {
                "I": "q6_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr6",
                "integW_sin": "integW_sin_rr6",
                "integW_minus_sin": "integW_minus_sin_rr6",
            },
            "digital_marker": "ON",
        },
        "q6_d_X180": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_X180_I_wf",
                "Q": "q6_d_X180_Q_wf",
            },
        },
        "q6_d_X90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_X90_I_wf",
                "Q": "q6_d_X90_Q_wf",
            },
        },
        "q6_d_mX90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_mX90_I_wf",
                "Q": "q6_d_mX90_Q_wf",
            },
        },
        "q6_d_Y180": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_Y180_I_wf",
                "Q": "q6_d_Y180_Q_wf",
            },
        },
        "q6_d_Y90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_Y90_I_wf",
                "Q": "q6_d_Y90_Q_wf",
            },
        },
        "q6_d_Y360": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_Y360_I_wf",
                "Q": "q6_d_Y360_Q_wf",
            },
        },
        "q6_d_X360": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_X360_I_wf",
                "Q": "q6_d_X360_Q_wf",
            },
        },
        "q6_d_mY90": {
            "operation": "control",
            "length": 96,
            "waveforms": {
                "I": "q6_d_mY90_I_wf",
                "Q": "q6_d_mY90_Q_wf",
            },
        },
        "q7_grft": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_X180": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_X360": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_Y360": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y360_Q_wf",
            },
        },
        "q7_X90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_mX90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q7_Y180": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y180_Q_wf",
            },
        },
        "q7_Y90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y90_Q_wf",
            },
        },
        "q7_mY90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_mY90_Q_wf",
            },
        },
        "q7_ro_pulse": {
            "operation": "measurement",
            "length": 3200,
            "waveforms": {
                "I": "q7_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr7",
                "integW_sin": "integW_sin_rr7",
                "integW_minus_sin": "integW_minus_sin_rr7",
            },
            "digital_marker": "ON",
        },
        "q7_d_X180": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_X180_I_wf",
                "Q": "q7_d_X180_Q_wf",
            },
        },
        "q7_d_X90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_X90_I_wf",
                "Q": "q7_d_X90_Q_wf",
            },
        },
        "q7_d_mX90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_mX90_I_wf",
                "Q": "q7_d_mX90_Q_wf",
            },
        },
        "q7_d_Y180": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_Y180_I_wf",
                "Q": "q7_d_Y180_Q_wf",
            },
        },
        "q7_d_Y90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_Y90_I_wf",
                "Q": "q7_d_Y90_Q_wf",
            },
        },
        "q7_d_Y360": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_Y360_I_wf",
                "Q": "q7_d_Y360_Q_wf",
            },
        },
        "q7_d_X360": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_X360_I_wf",
                "Q": "q7_d_X360_Q_wf",
            },
        },
        "q7_d_mY90": {
            "operation": "control",
            "length": 512,
            "waveforms": {
                "I": "q7_d_mY90_I_wf",
                "Q": "q7_d_mY90_Q_wf",
            },
        },
        "q8_grft": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_X180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_X360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_Y360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y360_Q_wf",
            },
        },
        "q8_X90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_mX90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q8_Y180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y180_Q_wf",
            },
        },
        "q8_Y90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y90_Q_wf",
            },
        },
        "q8_mY90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_mY90_Q_wf",
            },
        },
        "q8_ro_pulse": {
            "operation": "measurement",
            "length": 2000,
            "waveforms": {
                "I": "q8_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr8",
                "integW_sin": "integW_sin_rr8",
                "integW_minus_sin": "integW_minus_sin_rr8",
            },
            "digital_marker": "ON",
        },
        "q8_d_X180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_X180_I_wf",
                "Q": "q8_d_X180_Q_wf",
            },
        },
        "q8_d_X90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_X90_I_wf",
                "Q": "q8_d_X90_Q_wf",
            },
        },
        "q8_d_mX90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_mX90_I_wf",
                "Q": "q8_d_mX90_Q_wf",
            },
        },
        "q8_d_Y180": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y180_I_wf",
                "Q": "q8_d_Y180_Q_wf",
            },
        },
        "q8_d_Y90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y90_I_wf",
                "Q": "q8_d_Y90_Q_wf",
            },
        },
        "q8_d_Y360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y360_I_wf",
                "Q": "q8_d_Y360_Q_wf",
            },
        },
        "q8_d_X360": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_X360_I_wf",
                "Q": "q8_d_X360_Q_wf",
            },
        },
        "q8_d_mY90": {
            "operation": "control",
            "length": 300,
            "waveforms": {
                "I": "q8_d_mY90_I_wf",
                "Q": "q8_d_mY90_Q_wf",
            },
        },
        "rise_pulse": {
            "operation": "control",
            "length": 16,
            "waveforms": {
                "I": "rise_wf",
                "Q": "zero_wf",
            },
        },
        "fall_pulse": {
            "operation": "control",
            "length": 16,
            "waveforms": {
                "I": "fall_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_1_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_1_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y180_Q_wf",
            },
        },
        "q12_1_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y90_Q_wf",
            },
        },
        "q12_1_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_mY90_Q_wf",
            },
        },
        "q12_2_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_2_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_2_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y180_Q_wf",
            },
        },
        "q12_2_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y90_Q_wf",
            },
        },
        "q12_2_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_mY90_Q_wf",
            },
        },
        "q12_3_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_3_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_3_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_3_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_3_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_3_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_3_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y180_Q_wf",
            },
        },
        "q12_3_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y90_Q_wf",
            },
        },
        "q12_3_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_mY90_Q_wf",
            },
        },
        "q12_4_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_4_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_4_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y180_Q_wf",
            },
        },
        "q12_4_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y90_Q_wf",
            },
        },
        "q12_4_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_mY90_Q_wf",
            },
        },
        "q12_5_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_5_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_5_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_5_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_5_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_5_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_5_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y180_Q_wf",
            },
        },
        "q12_5_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y90_Q_wf",
            },
        },
        "q12_5_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_mY90_Q_wf",
            },
        },
        "q12_6_grft": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_6_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_6_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_6_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_6_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_6_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_6_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y180_Q_wf",
            },
        },
        "q12_6_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y90_Q_wf",
            },
        },
        "q12_6_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_mY90_Q_wf",
            },
        },
        "q12_7_grft": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_X180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_X360": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_X90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_mX90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "q12_7_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_7_Y180": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y180_Q_wf",
            },
        },
        "q12_7_Y90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y90_Q_wf",
            },
        },
        "q12_7_mY90": {
            "operation": "control",
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_mY90_Q_wf",
            },
        },
        "q12_8_grft": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_grft_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_X180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_X180_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_X360": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_X360_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_X90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_X90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_mX90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "q12_8_mX90_I_wf",
                "Q": "zero_wf",
            },
        },
        "q12_8_Y180": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y180_Q_wf",
            },
        },
        "q12_8_Y90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y90_Q_wf",
            },
        },
        "q12_8_mY90": {
            "operation": "control",
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_mY90_Q_wf",
            },
        },
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": 0.4,
        },
        "q1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0018102325287692638+0j), (0.0049207221882389554+0j), (0.01196928990414829+0j), (0.026052714666758268+0j), (0.05074375921832951+0j), (0.08844175456611598+0j), (0.13793583859088626+0j), (0.1925049702021102+0j), (0.24040961431410787+0j), (0.26866232830489245+0j)] + [(0.27241978256242366+0j)] * 32 + [(0.26866232830489245+0j), (0.24040961431410787+0j), (0.1925049702021102+0j), (0.13793583859088626+0j), (0.08844175456611598+0j), (0.05074375921832951+0j), (0.026052714666758268+0j), (0.01196928990414829+0j), (0.0049207221882389554+0j), (0.0018102325287692638+0j)],
        },
        "q1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q1_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0009016360704760211+0j), (0.002450900946258187+0j), (0.005961633847615021+0j), (0.012976270674651555+0j), (0.025274324118958358+0j), (0.044050846941311166+0j), (0.06870273597914867+0j), (0.09588239196990901+0j), (0.11974261676879687+0j), (0.13381465758017974+0j)] + [(0.13568616095773597+0j)] * 32 + [(0.13381465758017974+0j), (0.11974261676879687+0j), (0.09588239196990901+0j), (0.06870273597914867+0j), (0.044050846941311166+0j), (0.025274324118958358+0j), (0.012976270674651555+0j), (0.005961633847615021+0j), (0.002450900946258187+0j), (0.0009016360704760211+0j)],
        },
        "q1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0009016360704760211+0j), (-0.002450900946258187+0j), (-0.005961633847615021+0j), (-0.012976270674651555+0j), (-0.025274324118958358+0j), (-0.044050846941311166+0j), (-0.06870273597914867+0j), (-0.09588239196990901+0j), (-0.11974261676879687+0j), (-0.13381465758017974+0j)] + [(-0.13568616095773597+0j)] * 32 + [(-0.13381465758017974+0j), (-0.11974261676879687+0j), (-0.09588239196990901+0j), (-0.06870273597914867+0j), (-0.044050846941311166+0j), (-0.025274324118958358+0j), (-0.012976270674651555+0j), (-0.005961633847615021+0j), (-0.002450900946258187+0j), (-0.0009016360704760211+0j)],
        },
        "q1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0018131326903597729+0j), (0.004928605644790031+0j), (0.011988465824530895+0j), (0.02609445354903125+0j), (0.05082505546016817+0j), (0.08858344651757166+0j), (0.1381568246877983+0j), (0.19281338114473193+0j), (0.24079477297098875+0j), (0.2690927504484478+0j)] + [(0.27285622449865354+0j)] * 32 + [(0.2690927504484478+0j), (0.24079477297098875+0j), (0.19281338114473193+0j), (0.1381568246877983+0j), (0.08858344651757166+0j), (0.05082505546016817+0j), (0.02609445354903125+0j), (0.011988465824530895+0j), (0.004928605644790031+0j), (0.0018131326903597729+0j)],
        },
        "q1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.000892645569545443+0j), (0.0024264622309498524+0j), (0.005902188494428949+0j), (0.012846880139605308+0j), (0.025022305769258506+0j), (0.04361160189179854+0j), (0.06801767907872132+0j), (0.09492631804778165+0j), (0.1185486249324661+0j), (0.13248034893515798+0j)] + [(0.13433319095542334+0j)] * 32 + [(0.13248034893515798+0j), (0.1185486249324661+0j), (0.09492631804778165+0j), (0.06801767907872132+0j), (0.04361160189179854+0j), (0.025022305769258506+0j), (0.012846880139605308+0j), (0.005902188494428949+0j), (0.0024264622309498524+0j), (0.000892645569545443+0j)],
        },
        "q1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.000892645569545443+0j), (-0.0024264622309498524+0j), (-0.005902188494428949+0j), (-0.012846880139605308+0j), (-0.025022305769258506+0j), (-0.04361160189179854+0j), (-0.06801767907872132+0j), (-0.09492631804778165+0j), (-0.1185486249324661+0j), (-0.13248034893515798+0j)] + [(-0.13433319095542334+0j)] * 32 + [(-0.13248034893515798+0j), (-0.1185486249324661+0j), (-0.09492631804778165+0j), (-0.06801767907872132+0j), (-0.04361160189179854+0j), (-0.025022305769258506+0j), (-0.012846880139605308+0j), (-0.005902188494428949+0j), (-0.0024264622309498524+0j), (-0.000892645569545443+0j)],
        },
        "q1_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0005187064943764417+0j), (0.0005429527587189518+0j), (0.0005682019271479149+0j), (0.0005944887771340143+0j), (0.0006218489681410942+0j), (0.0006503190489357455+0j), (0.0006799364641902206+0j), (0.0007107395603368492+0j), (0.0007427675906314458+0j), (0.0007760607193825638+0j), (0.0008106600253028521+0j), (0.0008466075039382395+0j), (0.0008839460691301981+0j), (0.0009227195534659253+0j), (0.000962972707670938+0j), (0.0010047511988982892+0j), (0.0010481016078684325+0j), (0.0010930714248136078+0j), (0.0011397090441806173+0j), (0.00118806375804585+0j), (0.0012381857481965986+0j), (0.0012901260768328838+0j), (0.001343936675844356+0j), (0.001399670334617225+0j), (0.0014573806863267236+0j), (0.001517122192671188+0j), (0.0015789501270046106+0j), (0.0016429205558253315+0j), (0.001709090318579508+0j), (0.0017775170057390559+0j), (0.0018482589351149718+0j), (0.0019213751263682357+0j), (0.001996925273681932+0j), (0.0020749697165598096+0j), (0.0021555694087181548+0j), (0.0022387858850397083+0j), (0.0023246812265602704+0j), (0.002413318023460737+0j), (0.002504759336039516+0j), (0.0025990686536426105+0j), (0.002696309851531143+0j), (0.002796547145668675+0j), (0.0028998450454134615+0j), (0.003006268304103581+0j), (0.0031158818675259786+0j), (0.00322875082026346+0j), (0.0033449403299170726+0j), (0.003464515589204558+0j), (0.0035875417559391547+0j), (0.0037140838908965926+0j), (0.003844206893581887+0j), (0.003977975435911384+0j), (0.004115453893829432+0j), (0.004256706276883158+0j), (0.004401796155782963+0j), (0.004550786587980574+0j), (0.0047037400413008894+0j), (0.0048607183156681895+0j), (0.005021782462971869+0j), (0.005186992705121326+0j), (0.00535640835034431+0j), (0.005530087707787693+0j), (0.005708088000484348+0j), (0.0058904652767545725+0j), (0.0060772743201152725+0j), (0.0062685685577749325+0j), (0.006464399967797199+0j), (0.00666481898502072+0j), (0.006869874405827684+0j), (0.007079613291858256+0j), (0.007294080872772903+0j), (0.007513320448169221+0j), (0.007737373288764626+0j), (0.007966278536960766+0j), (0.00820007310691006+0j), (0.00843879158420916+0j), (0.008682466125348514+0j), (0.00893112635705128+0j), (0.00918479927563906+0j), (0.009443509146565776+0j), (0.009707277404264818+0j), (0.009976122552458232+0j), (0.01025006006508018+0j), (0.010529102287970132+0j), (0.010813258341494367+0j), (0.01110253402425719+0j), (0.011396931718065948+0j), (0.01169645029431623+0j), (0.012001085021965981+0j), (0.012310827477268957+0j), (0.01262566545543974+0j), (0.012945582884423795+0j), (0.013270559740947225+0j), (0.013600571969021494+0j), (0.013935591401079082+0j), (0.014275585681915955+0j), (0.014620518195616751+0j), (0.01497034799563796+0j), (0.015325029738223628+0j), (0.015684513619326875+0j), (0.01604874531520895+0j), (0.016417665926885826+0j), (0.016791211928589855+0j), (0.01716931512041152+0j), (0.01755190258528343+0j), (0.017938896650465122+0j), (0.01833021485368369+0j), (0.018725769914081154+0j), (0.019125469708114917+0j), (0.019529217250552962+0j), (0.019936910680700123+0j), (0.020348443253986236+0j), (0.02076370333904112+0j), (0.021182574420374876+0j), (0.02160493510677562+0j), (0.022030659145529444+0j), (0.02245961544256044+0j), (0.022891668088580716+0j), (0.02332667639133243+0j), (0.023764494913995703+0j), (0.02420497351982752+0j), (0.02464795742308804+0j), (0.02509328724630143+0j), (0.025540799083889155+0j), (0.025990324572203818+0j), (0.026441690965981892+0j), (0.026894721221223602+0j), (0.027349234084497978+0j), (0.027805044188660435+0j), (0.028261962154960064+0j), (0.028719794701502533+0j), (0.029178344758024135+0j), (0.029637411586921195+0j), (0.0300967909104682+0j), (0.030556275044146874+0j), (0.031015653035997282+0j), (0.031474710811890856+0j), (0.03193323132661429+0j), (0.032390994720641934+0j), (0.032847778482463424+0j), (0.033303357616322325+0j), (0.0337575048152107+0j), (0.034209990638953774+0j), (0.03466058369720844+0j), (0.03510905083718876+0j), (0.03555515733592173+0j), (0.03599866709682636+0j), (0.036439342850399604+0j), (0.036876946358783184+0j), (0.037311238623976305+0j), (0.03774198009945037+0j), (0.038168930904913356+0j), (0.038591851043963565+0j), (0.03901050062436454+0j), (0.03942464008066584+0j), (0.03983403039888727+0j), (0.04023843334297811+0j), (0.04063761168275637+0j), (0.0410313294230282+0j), (0.04141935203358215+0j), (0.04180144667974872+0j), (0.04217738245321173+0j), (0.04254693060275434+0j), (0.04290986476462021+0j), (0.043265961192167315+0j), (0.04361499898449094+0j), (0.043956760313690696+0j), (0.04429103065045601+0j), (0.04461759898764486+0j), (0.04493625806153063+0j), (0.04524680457039379+0j), (0.04554903939013658+0j), (0.04584276778660145+0j), (0.04612779962427714+0j), (0.046403949571079926+0j), (0.04667103729890175+0j), (0.04692888767962196+0j), (0.04717733097628471+0j), (0.04741620302915028+0j), (0.04764534543633499+0j), (0.0478646057287616+0j), (0.04807383753915013+0j), (0.04827290076478668+0j), (0.04846166172381721+0j), (0.048639993304822174+0j), (0.048807775109437825+0j), (0.04896489358780022+0j), (0.0491112421665986+0j), (0.049246721369536145+0j), (0.04937123893000731+0j), (0.049484709895813384+0j), (0.049587056725749507+0j), (0.049678209377909864+0j), (0.04975810538956994+0j), (0.04982668994851846+0j), (0.0498839159557249+0j), (0.04992974407924243+0j), (0.049964142799259675+0j), (0.04998708844422928+0j), (0.049998565218015226+0j)] + [(0.05+0j)] * 2000 + [(0.049998565218015226+0j), (0.04998708844422928+0j), (0.049964142799259675+0j), (0.04992974407924243+0j), (0.0498839159557249+0j), (0.04982668994851846+0j), (0.04975810538956994+0j), (0.049678209377909864+0j), (0.049587056725749507+0j), (0.049484709895813384+0j), (0.04937123893000731+0j), (0.049246721369536145+0j), (0.0491112421665986+0j), (0.04896489358780022+0j), (0.048807775109437825+0j), (0.048639993304822174+0j), (0.04846166172381721+0j), (0.04827290076478668+0j), (0.04807383753915013+0j), (0.0478646057287616+0j), (0.04764534543633499+0j), (0.04741620302915028+0j), (0.04717733097628471+0j), (0.04692888767962196+0j), (0.04667103729890175+0j), (0.046403949571079926+0j), (0.04612779962427714+0j), (0.04584276778660145+0j), (0.04554903939013658+0j), (0.04524680457039379+0j), (0.04493625806153063+0j), (0.04461759898764486+0j), (0.04429103065045601+0j), (0.043956760313690696+0j), (0.04361499898449094+0j), (0.043265961192167315+0j), (0.04290986476462021+0j), (0.04254693060275434+0j), (0.04217738245321173+0j), (0.04180144667974872+0j), (0.04141935203358215+0j), (0.0410313294230282+0j), (0.04063761168275637+0j), (0.04023843334297811+0j), (0.03983403039888727+0j), (0.03942464008066584+0j), (0.03901050062436454+0j), (0.038591851043963565+0j), (0.038168930904913356+0j), (0.03774198009945037+0j), (0.037311238623976305+0j), (0.036876946358783184+0j), (0.036439342850399604+0j), (0.03599866709682636+0j), (0.03555515733592173+0j), (0.03510905083718876+0j), (0.03466058369720844+0j), (0.034209990638953774+0j), (0.0337575048152107+0j), (0.033303357616322325+0j), (0.032847778482463424+0j), (0.032390994720641934+0j), (0.03193323132661429+0j), (0.031474710811890856+0j), (0.031015653035997282+0j), (0.030556275044146874+0j), (0.0300967909104682+0j), (0.029637411586921195+0j), (0.029178344758024135+0j), (0.028719794701502533+0j), (0.028261962154960064+0j), (0.027805044188660435+0j), (0.027349234084497978+0j), (0.026894721221223602+0j), (0.026441690965981892+0j), (0.025990324572203818+0j), (0.025540799083889155+0j), (0.02509328724630143+0j), (0.02464795742308804+0j), (0.02420497351982752+0j), (0.023764494913995703+0j), (0.02332667639133243+0j), (0.022891668088580716+0j), (0.02245961544256044+0j), (0.022030659145529444+0j), (0.02160493510677562+0j), (0.021182574420374876+0j), (0.02076370333904112+0j), (0.020348443253986236+0j), (0.019936910680700123+0j), (0.019529217250552962+0j), (0.019125469708114917+0j), (0.018725769914081154+0j), (0.01833021485368369+0j), (0.017938896650465122+0j), (0.01755190258528343+0j), (0.01716931512041152+0j), (0.016791211928589855+0j), (0.016417665926885826+0j), (0.01604874531520895+0j), (0.015684513619326875+0j), (0.015325029738223628+0j), (0.01497034799563796+0j), (0.014620518195616751+0j), (0.014275585681915955+0j), (0.013935591401079082+0j), (0.013600571969021494+0j), (0.013270559740947225+0j), (0.012945582884423795+0j), (0.01262566545543974+0j), (0.012310827477268957+0j), (0.012001085021965981+0j), (0.01169645029431623+0j), (0.011396931718065948+0j), (0.01110253402425719+0j), (0.010813258341494367+0j), (0.010529102287970132+0j), (0.01025006006508018+0j), (0.009976122552458232+0j), (0.009707277404264818+0j), (0.009443509146565776+0j), (0.00918479927563906+0j), (0.00893112635705128+0j), (0.008682466125348514+0j), (0.00843879158420916+0j), (0.00820007310691006+0j), (0.007966278536960766+0j), (0.007737373288764626+0j), (0.007513320448169221+0j), (0.007294080872772903+0j), (0.007079613291858256+0j), (0.006869874405827684+0j), (0.00666481898502072+0j), (0.006464399967797199+0j), (0.0062685685577749325+0j), (0.0060772743201152725+0j), (0.0058904652767545725+0j), (0.005708088000484348+0j), (0.005530087707787693+0j), (0.00535640835034431+0j), (0.005186992705121326+0j), (0.005021782462971869+0j), (0.0048607183156681895+0j), (0.0047037400413008894+0j), (0.004550786587980574+0j), (0.004401796155782963+0j), (0.004256706276883158+0j), (0.004115453893829432+0j), (0.003977975435911384+0j), (0.003844206893581887+0j), (0.0037140838908965926+0j), (0.0035875417559391547+0j), (0.003464515589204558+0j), (0.0033449403299170726+0j), (0.00322875082026346+0j), (0.0031158818675259786+0j), (0.003006268304103581+0j), (0.0028998450454134615+0j), (0.002796547145668675+0j), (0.002696309851531143+0j), (0.0025990686536426105+0j), (0.002504759336039516+0j), (0.002413318023460737+0j), (0.0023246812265602704+0j), (0.0022387858850397083+0j), (0.0021555694087181548+0j), (0.0020749697165598096+0j), (0.001996925273681932+0j), (0.0019213751263682357+0j), (0.0018482589351149718+0j), (0.0017775170057390559+0j), (0.001709090318579508+0j), (0.0016429205558253315+0j), (0.0015789501270046106+0j), (0.001517122192671188+0j), (0.0014573806863267236+0j), (0.001399670334617225+0j), (0.001343936675844356+0j), (0.0012901260768328838+0j), (0.0012381857481965986+0j), (0.00118806375804585+0j), (0.0011397090441806173+0j), (0.0010930714248136078+0j), (0.0010481016078684325+0j), (0.0010047511988982892+0j), (0.000962972707670938+0j), (0.0009227195534659253+0j), (0.0008839460691301981+0j), (0.0008466075039382395+0j), (0.0008106600253028521+0j), (0.0007760607193825638+0j), (0.0007427675906314458+0j), (0.0007107395603368492+0j), (0.0006799364641902206+0j), (0.0006503190489357455+0j), (0.0006218489681410942+0j), (0.0005944887771340143+0j), (0.0005682019271479149+0j), (0.0005429527587189518+0j), (0.0005187064943764417+0j)],
        },
        "q1_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0018102325287692638, 0.0049207221882389554, 0.01196928990414829, 0.026052714666758268, 0.05074375921832951, 0.08844175456611598, 0.13793583859088626, 0.1925049702021102, 0.24040961431410787, 0.26866232830489245] + [0.27241978256242366] * 32 + [0.26866232830489245, 0.24040961431410787, 0.1925049702021102, 0.13793583859088626, 0.08844175456611598, 0.05074375921832951, 0.026052714666758268, 0.01196928990414829, 0.0049207221882389554, 0.0018102325287692638],
        },
        "q1_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000745215354671824, -0.0018124732140622308, -0.0038900346892047533, -0.007338210481279233, -0.012093977377148428, -0.017246210727192103, -0.0209203520515165, -0.020854788043051208, -0.01562668707650058, -0.0058210402630838156] + [0.0] * 32 + [0.0058210402630838156, 0.01562668707650058, 0.020854788043051208, 0.0209203520515165, 0.017246210727192103, 0.012093977377148428, 0.007338210481279233, 0.0038900346892047533, 0.0018124732140622308, 0.000745215354671824],
        },
        "q1_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009016360704760211, 0.002450900946258187, 0.005961633847615021, 0.012976270674651555, 0.025274324118958358, 0.044050846941311166, 0.06870273597914867, 0.09588239196990901, 0.11974261676879687, 0.13381465758017974] + [0.13568616095773597] * 32 + [0.13381465758017974, 0.11974261676879687, 0.09588239196990901, 0.06870273597914867, 0.044050846941311166, 0.025274324118958358, 0.012976270674651555, 0.005961633847615021, 0.002450900946258187, 0.0009016360704760211],
        },
        "q1_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0003711749918125249, -0.0009027521053779559, -0.0019375387059112137, -0.0036549974423257634, -0.006023737870941716, -0.008589949315096471, -0.010419956396170008, -0.010387300439535813, -0.007783301043536984, -0.002899329111303676] + [0.0] * 32 + [0.002899329111303676, 0.007783301043536984, 0.010387300439535813, 0.010419956396170008, 0.008589949315096471, 0.006023737870941716, 0.0036549974423257634, 0.0019375387059112137, 0.0009027521053779559, 0.0003711749918125249],
        },
        "q1_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0009016360704760211, -0.002450900946258187, -0.005961633847615021, -0.012976270674651555, -0.025274324118958358, -0.044050846941311166, -0.06870273597914867, -0.09588239196990901, -0.11974261676879687, -0.13381465758017974] + [-0.13568616095773597] * 32 + [-0.13381465758017974, -0.11974261676879687, -0.09588239196990901, -0.06870273597914867, -0.044050846941311166, -0.025274324118958358, -0.012976270674651555, -0.005961633847615021, -0.002450900946258187, -0.0009016360704760211],
        },
        "q1_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003711749918125249, 0.0009027521053779559, 0.0019375387059112137, 0.0036549974423257634, 0.006023737870941716, 0.008589949315096471, 0.010419956396170008, 0.010387300439535813, 0.007783301043536984, 0.002899329111303676] + [0.0] * 32 + [-0.002899329111303676, -0.007783301043536984, -0.010387300439535813, -0.010419956396170008, -0.008589949315096471, -0.006023737870941716, -0.0036549974423257634, -0.0019375387059112137, -0.0009027521053779559, -0.0003711749918125249],
        },
        "q1_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007464092592746466, 0.0018153769654398635, 0.003896266888114055, 0.007349966979874109, 0.012113353058508842, 0.017273840767608423, 0.020953868409506696, 0.020888199361376036, 0.01565172248876167, 0.005830366113282343] + [0.0] * 32 + [-0.005830366113282343, -0.01565172248876167, -0.020888199361376036, -0.020953868409506696, -0.017273840767608423, -0.012113353058508842, -0.007349966979874109, -0.003896266888114055, -0.0018153769654398635, -0.0007464092592746466],
        },
        "q1_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0018131326903597729, 0.004928605644790031, 0.011988465824530895, 0.02609445354903125, 0.05082505546016817, 0.08858344651757166, 0.1381568246877983, 0.19281338114473193, 0.24079477297098875, 0.2690927504484478] + [0.27285622449865354] * 32 + [0.2690927504484478, 0.24079477297098875, 0.19281338114473193, 0.1381568246877983, 0.08858344651757166, 0.05082505546016817, 0.02609445354903125, 0.011988465824530895, 0.004928605644790031, 0.0018131326903597729],
        },
        "q1_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00036747388754377485, 0.0008937504761072936, 0.0019182188892923765, 0.0036185522966816434, 0.00596367325872443, 0.008504296189805886, 0.010316055686400389, 0.010283725352728852, 0.00770569126552761, 0.002870418975688243] + [0.0] * 32 + [-0.002870418975688243, -0.00770569126552761, -0.010283725352728852, -0.010316055686400389, -0.008504296189805886, -0.00596367325872443, -0.0036185522966816434, -0.0019182188892923765, -0.0008937504761072936, -0.00036747388754377485],
        },
        "q1_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000892645569545443, 0.0024264622309498524, 0.005902188494428949, 0.012846880139605308, 0.025022305769258506, 0.04361160189179854, 0.06801767907872132, 0.09492631804778165, 0.1185486249324661, 0.13248034893515798] + [0.13433319095542334] * 32 + [0.13248034893515798, 0.1185486249324661, 0.09492631804778165, 0.06801767907872132, 0.04361160189179854, 0.025022305769258506, 0.012846880139605308, 0.005902188494428949, 0.0024264622309498524, 0.000892645569545443],
        },
        "q1_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002552277098571049, 0.0006207512831054925, 0.001332292254535805, 0.002513252905814174, 0.004142048509444026, 0.005906629325361513, 0.007164980579156634, 0.007142525658408233, 0.0053519610541911695, 0.0019936395110741463] + [0.0] * 32 + [-0.0019936395110741463, -0.0053519610541911695, -0.007142525658408233, -0.007164980579156634, -0.005906629325361513, -0.004142048509444026, -0.002513252905814174, -0.001332292254535805, -0.0006207512831054925, -0.0002552277098571049],
        },
        "q1_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q1_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q1_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002552277098571049, -0.0006207512831054925, -0.001332292254535805, -0.002513252905814174, -0.004142048509444026, -0.005906629325361513, -0.007164980579156634, -0.007142525658408233, -0.0053519610541911695, -0.0019936395110741463] + [0.0] * 32 + [0.0019936395110741463, 0.0053519610541911695, 0.007142525658408233, 0.007164980579156634, 0.005906629325361513, 0.004142048509444026, 0.002513252905814174, 0.001332292254535805, 0.0006207512831054925, 0.0002552277098571049],
        },
        "q1_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00036747388754377485, -0.0008937504761072936, -0.0019182188892923765, -0.0036185522966816434, -0.00596367325872443, -0.008504296189805886, -0.010316055686400389, -0.010283725352728852, -0.00770569126552761, -0.002870418975688243] + [0.0] * 32 + [0.002870418975688243, 0.00770569126552761, 0.010283725352728852, 0.010316055686400389, 0.008504296189805886, 0.00596367325872443, 0.0036185522966816434, 0.0019182188892923765, 0.0008937504761072936, 0.00036747388754377485],
        },
        "q1_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000892645569545443, -0.0024264622309498524, -0.005902188494428949, -0.012846880139605308, -0.025022305769258506, -0.04361160189179854, -0.06801767907872132, -0.09492631804778165, -0.1185486249324661, -0.13248034893515798] + [-0.13433319095542334] * 32 + [-0.13248034893515798, -0.1185486249324661, -0.09492631804778165, -0.06801767907872132, -0.04361160189179854, -0.025022305769258506, -0.012846880139605308, -0.005902188494428949, -0.0024264622309498524, -0.000892645569545443],
        },
        "q2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.001728015332229015+0j), (0.004697232676896751+0j), (0.011425668327993303+0j), (0.024869451672572557+0j), (0.04843907760503372+0j), (0.08442490424331768+0j), (0.13167106444108065+0j), (0.18376177355828333+0j), (0.22949068307400539+0j), (0.2564602144337967+0j)] + [(0.2600470125185585+0j)] * 32 + [(0.2564602144337967+0j), (0.22949068307400539+0j), (0.18376177355828333+0j), (0.13167106444108065+0j), (0.08442490424331768+0j), (0.04843907760503372+0j), (0.024869451672572557+0j), (0.011425668327993303+0j), (0.004697232676896751+0j), (0.001728015332229015+0j)],
        },
        "q2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0023019196663695667+0j), (0.006257266399664901+0j), (0.015220334064800986+0j), (0.03312903469616625+0j), (0.06452654862500447+0j), (0.11246390224927966+0j), (0.1754013445805286+0j), (0.24479229587339238+0j), (0.30570858184181127+0j), (0.3416351696862567+0j)] + [(0.34641320660330166+0j)] * 32 + [(0.3416351696862567+0j), (0.30570858184181127+0j), (0.24479229587339238+0j), (0.1754013445805286+0j), (0.11246390224927966+0j), (0.06452654862500447+0j), (0.03312903469616625+0j), (0.015220334064800986+0j), (0.006257266399664901+0j), (0.0023019196663695667+0j)],
        },
        "q2_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0023019196663695667+0j), (0.006257266399664901+0j), (0.015220334064800986+0j), (0.03312903469616625+0j), (0.06452654862500447+0j), (0.11246390224927966+0j), (0.1754013445805286+0j), (0.24479229587339238+0j), (0.30570858184181127+0j), (0.3416351696862567+0j)] + [(0.34641320660330166+0j)] * 32 + [(0.3416351696862567+0j), (0.30570858184181127+0j), (0.24479229587339238+0j), (0.1754013445805286+0j), (0.11246390224927966+0j), (0.06452654862500447+0j), (0.03312903469616625+0j), (0.015220334064800986+0j), (0.006257266399664901+0j), (0.0023019196663695667+0j)],
        },
        "q2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0008599720895460722+0j), (0.002337646503995043+0j), (0.005686150859443048+0j), (0.012376646156917807+0j), (0.024106415033917344+0j), (0.042015287687407414+0j), (0.06552802993598945+0j), (0.0914517327700801+0j), (0.11420939303815864+0j), (0.1276311745495765+0j)] + [(0.1294161970468906+0j)] * 32 + [(0.1276311745495765+0j), (0.11420939303815864+0j), (0.0914517327700801+0j), (0.06552802993598945+0j), (0.042015287687407414+0j), (0.024106415033917344+0j), (0.012376646156917807+0j), (0.005686150859443048+0j), (0.002337646503995043+0j), (0.0008599720895460722+0j)],
        },
        "q2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0008599720895460722+0j), (-0.002337646503995043+0j), (-0.005686150859443048+0j), (-0.012376646156917807+0j), (-0.024106415033917344+0j), (-0.042015287687407414+0j), (-0.06552802993598945+0j), (-0.0914517327700801+0j), (-0.11420939303815864+0j), (-0.1276311745495765+0j)] + [(-0.1294161970468906+0j)] * 32 + [(-0.1276311745495765+0j), (-0.11420939303815864+0j), (-0.0914517327700801+0j), (-0.06552802993598945+0j), (-0.042015287687407414+0j), (-0.024106415033917344+0j), (-0.012376646156917807+0j), (-0.005686150859443048+0j), (-0.002337646503995043+0j), (-0.0008599720895460722+0j)],
        },
        "q2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0017221707040954192+0j), (0.004681345330447098+0j), (0.011387023542088086+0j), (0.024785336274866496+0j), (0.04827524318154477+0j), (0.08413935575233286+0j), (0.13122571630483457+0j), (0.18314024016584937+0j), (0.22871448179981746+0j), (0.25559279470870994+0j)] + [(0.25916746124544393+0j)] * 32 + [(0.25559279470870994+0j), (0.22871448179981746+0j), (0.18314024016584937+0j), (0.13122571630483457+0j), (0.08413935575233286+0j), (0.04827524318154477+0j), (0.024785336274866496+0j), (0.011387023542088086+0j), (0.004681345330447098+0j), (0.0017221707040954192+0j)],
        },
        "q2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0008570497754792741+0j), (0.0023297028307702155+0j), (0.005666828466490438+0j), (0.01233458845806477+0j), (0.024024497822172863+0j), (0.04187251344191499+0j), (0.0653053558678664+0j), (0.09114096607386311+0j), (0.11382129240106464+0j), (0.1271974646870331+0j)] + [(0.1289764214103333+0j)] * 32 + [(0.1271974646870331+0j), (0.11382129240106464+0j), (0.09114096607386311+0j), (0.0653053558678664+0j), (0.04187251344191499+0j), (0.024024497822172863+0j), (0.01233458845806477+0j), (0.005666828466490438+0j), (0.0023297028307702155+0j), (0.0008570497754792741+0j)],
        },
        "q2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0008570497754792741+0j), (-0.0023297028307702155+0j), (-0.005666828466490438+0j), (-0.01233458845806477+0j), (-0.024024497822172863+0j), (-0.04187251344191499+0j), (-0.0653053558678664+0j), (-0.09114096607386311+0j), (-0.11382129240106464+0j), (-0.1271974646870331+0j)] + [(-0.1289764214103333+0j)] * 32 + [(-0.1271974646870331+0j), (-0.11382129240106464+0j), (-0.09114096607386311+0j), (-0.0653053558678664+0j), (-0.04187251344191499+0j), (-0.024024497822172863+0j), (-0.01233458845806477+0j), (-0.005666828466490438+0j), (-0.0023297028307702155+0j), (-0.0008570497754792741+0j)],
        },
        "q2_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0016598607820046136+0j), (0.001737448827900646+0j), (0.001818246166873328+0j), (0.001902364086828846+0j), (0.001989916698051502+0j), (0.002081020956594386+0j), (0.002175796685408706+0j), (0.002274366593077918+0j), (0.002376856290020627+0j), (0.002483394302024204+0j), (0.0025941120809691268+0j), (0.0027091440126023668+0j), (0.0028286274212166347+0j), (0.0029527025710909616+0j), (0.003081512664547002+0j), (0.003215203836474526+0j), (0.0033539251451789845+0j), (0.0034978285594035458+0j), (0.003647068941377976+0j), (0.003801804025746721+0j), (0.003962194394229116+0j), (0.0041284034458652285+0j), (0.004300597362701939+0j), (0.00447894507077512+0j), (0.004663618196245516+0j), (0.004854791016547802+0j), (0.005052640406414754+0j), (0.005257345778641061+0j), (0.005469089019454426+0j), (0.0056880544183649795+0j), (0.005914428592367911+0j), (0.006148400404378355+0j), (0.006390160875782183+0j), (0.0066399030929913914+0j), (0.006897822107898096+0j), (0.007164114832127068+0j), (0.007438979924992866+0j), (0.0077226176750743595+0j), (0.008015229875326452+0j), (0.008317019691656356+0j), (0.008628191524899659+0j), (0.008948950866139761+0j), (0.009279504145323077+0j), (0.009620058573131461+0j), (0.009970821976083132+0j), (0.010332002624843073+0j), (0.010703809055734634+0j), (0.011086449885454588+0j), (0.011480133619005297+0j), (0.0118850684508691+0j), (0.01230146205946204+0j), (0.012729521394916432+0j), (0.013169452460254185+0j), (0.013621460086026108+0j), (0.014085747698505485+0j), (0.014562517081537838+0j), (0.015051968132162847+0j), (0.01555429861013821+0j), (0.016069703881509984+0j), (0.016598376656388247+0j), (0.017140506721101796+0j), (0.01769628066492062+0j), (0.018265881601549915+0j), (0.018849488885614635+0j), (0.019447277824368874+0j), (0.02005941938487979+0j), (0.02068607989695104+0j), (0.021327420752066305+0j), (0.021983598098648593+0j), (0.022654762533946424+0j), (0.023341058792873293+0j), (0.024042625434141512+0j), (0.024759594524046805+0j), (0.025492091318274457+0j), (0.026240233942112196+0j), (0.027004133069469315+0j), (0.027783891601115253+0j), (0.028579604342564104+0j), (0.029391357682045+0j), (0.030219229269010488+0j), (0.031063287693647423+0j), (0.031923592167866346+0j), (0.03280019220825658+0j), (0.033693127321504424+0j), (0.034602426692781976+0j), (0.03552810887762301+0j), (0.03647018149781104+0j), (0.03742864094181194+0j), (0.03840347207029115+0j), (0.03939464792726067+0j), (0.04040212945740717+0j), (0.04142586523015615+0j), (0.04246579117103112+0j), (0.043521830300868786+0j), (0.044593892483453065+0j), (0.04568187418213106+0j), (0.04678565822597361+0j), (0.04790511358604148+0j), (0.04904009516231562+0j), (0.050190443581846+0j), (0.05135598500866864+0j), (0.05253653096603466+0j), (0.053731878171487536+0j), (0.05494180838531687+0j), (0.056166088272906985+0j), (0.0574044692814884+0j), (0.05865668753178782+0j), (0.0599224637250597+0j), (0.061201503065967736+0j), (0.062493495201769486+0j), (0.0637981141782404+0j), (0.06511501841275597+0j), (0.06644385068493158+0j), (0.06778423814519961+0j), (0.06913579234168199+0j), (0.07049810926569422+0j), (0.07187076941619341+0j), (0.0732533378834583+0j), (0.07464536445226377+0j), (0.07604638372478625+0j), (0.07745591526344807+0j), (0.07887346375388174+0j), (0.08029851918816458+0j), (0.08173055706844531+0j), (0.08316903863105223+0j), (0.08461341109114207+0j), (0.08606310790791553+0j), (0.08751754907039354+0j), (0.0889761414037134+0j), (0.09043827889587222+0j), (0.09190334304480813+0j), (0.09337070322567724+0j), (0.09483971707814783+0j), (0.09630973091349825+0j), (0.09778008014127001+0j), (0.09925008971519132+0j), (0.10071907459805075+0j), (0.10218634024516575+0j), (0.10365118310605421+0j), (0.10511289114388297+0j), (0.10657074437223146+0j), (0.10802401540867426+0j), (0.1094719700446521+0j), (0.11091386783106702+0j), (0.11234896267900406+0j), (0.11377650347494955+0j), (0.11519573470984437+0j), (0.11660589712127875+0j), (0.1180062283481062+0j), (0.11939596359672419+0j), (0.1207743363182412+0j), (0.12214057889572276+0j), (0.12349392334068343+0j), (0.12483360199796656+0j), (0.1261588482581307+0j), (0.12746889727643929+0j), (0.12876298669752995+0j), (0.13004035738482042+0j), (0.13130025415369026+0j), (0.13254192650746288+0j), (0.13376462937519593+0j), (0.13496762385027755+0j), (0.13615017792881393+0j), (0.1373115672467847+0j), (0.13845107581493543+0j), (0.13956799675037102+0j), (0.14066163300381024+0j), (0.14173129808145926+0j), (0.14277631676046357+0j), (0.14379602579689804+0j), (0.14478977462526016+0j), (0.1457569260484371+0j), (0.14669685691712467+0j), (0.14760895879768687+0j), (0.1484926386274558+0j), (0.14934731935648562+0j), (0.1501724405747903+0j), (0.15096745912411108+0j), (0.15173184969328093+0j), (0.15246510539627198+0j), (0.15316673833203714+0j), (0.15383628012528044+0j), (0.1544732824473174+0j), (0.1550773175162151+0j), (0.15564797857543097+0j), (0.15618488035020106+0j), (0.15668765948096072+0j), (0.15715597493311556+0j), (0.15758950838251568+0j), (0.15798796457602343+0j), (0.15835107166660284+0j), (0.15867858152239844+0j), (0.15897027000931158+0j), (0.15922593724662384+0j), (0.1594454078352591+0j), (0.1596285310583197+0j), (0.1597751810535758+0j), (0.15988525695763098+0j), (0.1599586830215337+0j), (0.15999540869764875+0j)] + [(0.16000000000000003+0j)] * 1600 + [(0.15999540869764875+0j), (0.1599586830215337+0j), (0.15988525695763098+0j), (0.1597751810535758+0j), (0.1596285310583197+0j), (0.1594454078352591+0j), (0.15922593724662384+0j), (0.15897027000931158+0j), (0.15867858152239844+0j), (0.15835107166660284+0j), (0.15798796457602343+0j), (0.15758950838251568+0j), (0.15715597493311556+0j), (0.15668765948096072+0j), (0.15618488035020106+0j), (0.15564797857543097+0j), (0.1550773175162151+0j), (0.1544732824473174+0j), (0.15383628012528044+0j), (0.15316673833203714+0j), (0.15246510539627198+0j), (0.15173184969328093+0j), (0.15096745912411108+0j), (0.1501724405747903+0j), (0.14934731935648562+0j), (0.1484926386274558+0j), (0.14760895879768687+0j), (0.14669685691712467+0j), (0.1457569260484371+0j), (0.14478977462526016+0j), (0.14379602579689804+0j), (0.14277631676046357+0j), (0.14173129808145926+0j), (0.14066163300381024+0j), (0.13956799675037102+0j), (0.13845107581493543+0j), (0.1373115672467847+0j), (0.13615017792881393+0j), (0.13496762385027755+0j), (0.13376462937519593+0j), (0.13254192650746288+0j), (0.13130025415369026+0j), (0.13004035738482042+0j), (0.12876298669752995+0j), (0.12746889727643929+0j), (0.1261588482581307+0j), (0.12483360199796656+0j), (0.12349392334068343+0j), (0.12214057889572276+0j), (0.1207743363182412+0j), (0.11939596359672419+0j), (0.1180062283481062+0j), (0.11660589712127875+0j), (0.11519573470984437+0j), (0.11377650347494955+0j), (0.11234896267900406+0j), (0.11091386783106702+0j), (0.1094719700446521+0j), (0.10802401540867426+0j), (0.10657074437223146+0j), (0.10511289114388297+0j), (0.10365118310605421+0j), (0.10218634024516575+0j), (0.10071907459805075+0j), (0.09925008971519132+0j), (0.09778008014127001+0j), (0.09630973091349825+0j), (0.09483971707814783+0j), (0.09337070322567724+0j), (0.09190334304480813+0j), (0.09043827889587222+0j), (0.0889761414037134+0j), (0.08751754907039354+0j), (0.08606310790791553+0j), (0.08461341109114207+0j), (0.08316903863105223+0j), (0.08173055706844531+0j), (0.08029851918816458+0j), (0.07887346375388174+0j), (0.07745591526344807+0j), (0.07604638372478625+0j), (0.07464536445226377+0j), (0.0732533378834583+0j), (0.07187076941619341+0j), (0.07049810926569422+0j), (0.06913579234168199+0j), (0.06778423814519961+0j), (0.06644385068493158+0j), (0.06511501841275597+0j), (0.0637981141782404+0j), (0.062493495201769486+0j), (0.061201503065967736+0j), (0.0599224637250597+0j), (0.05865668753178782+0j), (0.0574044692814884+0j), (0.056166088272906985+0j), (0.05494180838531687+0j), (0.053731878171487536+0j), (0.05253653096603466+0j), (0.05135598500866864+0j), (0.050190443581846+0j), (0.04904009516231562+0j), (0.04790511358604148+0j), (0.04678565822597361+0j), (0.04568187418213106+0j), (0.044593892483453065+0j), (0.043521830300868786+0j), (0.04246579117103112+0j), (0.04142586523015615+0j), (0.04040212945740717+0j), (0.03939464792726067+0j), (0.03840347207029115+0j), (0.03742864094181194+0j), (0.03647018149781104+0j), (0.03552810887762301+0j), (0.034602426692781976+0j), (0.033693127321504424+0j), (0.03280019220825658+0j), (0.031923592167866346+0j), (0.031063287693647423+0j), (0.030219229269010488+0j), (0.029391357682045+0j), (0.028579604342564104+0j), (0.027783891601115253+0j), (0.027004133069469315+0j), (0.026240233942112196+0j), (0.025492091318274457+0j), (0.024759594524046805+0j), (0.024042625434141512+0j), (0.023341058792873293+0j), (0.022654762533946424+0j), (0.021983598098648593+0j), (0.021327420752066305+0j), (0.02068607989695104+0j), (0.02005941938487979+0j), (0.019447277824368874+0j), (0.018849488885614635+0j), (0.018265881601549915+0j), (0.01769628066492062+0j), (0.017140506721101796+0j), (0.016598376656388247+0j), (0.016069703881509984+0j), (0.01555429861013821+0j), (0.015051968132162847+0j), (0.014562517081537838+0j), (0.014085747698505485+0j), (0.013621460086026108+0j), (0.013169452460254185+0j), (0.012729521394916432+0j), (0.01230146205946204+0j), (0.0118850684508691+0j), (0.011480133619005297+0j), (0.011086449885454588+0j), (0.010703809055734634+0j), (0.010332002624843073+0j), (0.009970821976083132+0j), (0.009620058573131461+0j), (0.009279504145323077+0j), (0.008948950866139761+0j), (0.008628191524899659+0j), (0.008317019691656356+0j), (0.008015229875326452+0j), (0.0077226176750743595+0j), (0.007438979924992866+0j), (0.007164114832127068+0j), (0.006897822107898096+0j), (0.0066399030929913914+0j), (0.006390160875782183+0j), (0.006148400404378355+0j), (0.005914428592367911+0j), (0.0056880544183649795+0j), (0.005469089019454426+0j), (0.005257345778641061+0j), (0.005052640406414754+0j), (0.004854791016547802+0j), (0.004663618196245516+0j), (0.00447894507077512+0j), (0.004300597362701939+0j), (0.0041284034458652285+0j), (0.003962194394229116+0j), (0.003801804025746721+0j), (0.003647068941377976+0j), (0.0034978285594035458+0j), (0.0033539251451789845+0j), (0.003215203836474526+0j), (0.003081512664547002+0j), (0.0029527025710909616+0j), (0.0028286274212166347+0j), (0.0027091440126023668+0j), (0.0025941120809691268+0j), (0.002483394302024204+0j), (0.002376856290020627+0j), (0.002274366593077918+0j), (0.002175796685408706+0j), (0.002081020956594386+0j), (0.001989916698051502+0j), (0.001902364086828846+0j), (0.001818246166873328+0j), (0.001737448827900646+0j), (0.0016598607820046136+0j)],
        },
        "q2_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001728015332229015, 0.004697232676896751, 0.011425668327993303, 0.024869451672572557, 0.04843907760503372, 0.08442490424331768, 0.13167106444108065, 0.18376177355828333, 0.22949068307400539, 0.2564602144337967] + [0.2600470125185585] * 32 + [0.2564602144337967, 0.22949068307400539, 0.18376177355828333, 0.13167106444108065, 0.08442490424331768, 0.04843907760503372, 0.024869451672572557, 0.011425668327993303, 0.004697232676896751, 0.001728015332229015],
        },
        "q2_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006305845515305529, 0.001533674261655393, 0.003291660275855047, 0.0062094294439384605, 0.01023365293371905, 0.014593357462148685, 0.0177023336053996, 0.01764685480908194, 0.013222952801855325, 0.004925633967048994] + [0.0] * 32 + [-0.004925633967048994, -0.013222952801855325, -0.01764685480908194, -0.0177023336053996, -0.014593357462148685, -0.01023365293371905, -0.0062094294439384605, -0.003291660275855047, -0.001533674261655393, -0.0006305845515305529],
        },
        "q2_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008599720895460722, 0.002337646503995043, 0.005686150859443048, 0.012376646156917807, 0.024106415033917344, 0.042015287687407414, 0.06552802993598945, 0.0914517327700801, 0.11420939303815864, 0.1276311745495765] + [0.1294161970468906] * 32 + [0.1276311745495765, 0.11420939303815864, 0.0914517327700801, 0.06552802993598945, 0.042015287687407414, 0.024106415033917344, 0.012376646156917807, 0.005686150859443048, 0.002337646503995043, 0.0008599720895460722],
        },
        "q2_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003138196197111826, 0.0007632554149722213, 0.001638142852500863, 0.003090213329823024, 0.005092926974060729, 0.007262597661114692, 0.008809825084618847, 0.008782215250663696, 0.006580595749872409, 0.00245131374472136] + [0.0] * 32 + [-0.00245131374472136, -0.006580595749872409, -0.008782215250663696, -0.008809825084618847, -0.007262597661114692, -0.005092926974060729, -0.003090213329823024, -0.001638142852500863, -0.0007632554149722213, -0.0003138196197111826],
        },
        "q2_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008599720895460722, -0.002337646503995043, -0.005686150859443048, -0.012376646156917807, -0.024106415033917344, -0.042015287687407414, -0.06552802993598945, -0.0914517327700801, -0.11420939303815864, -0.1276311745495765] + [-0.1294161970468906] * 32 + [-0.1276311745495765, -0.11420939303815864, -0.0914517327700801, -0.06552802993598945, -0.042015287687407414, -0.024106415033917344, -0.012376646156917807, -0.005686150859443048, -0.002337646503995043, -0.0008599720895460722],
        },
        "q2_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0003138196197111826, -0.0007632554149722213, -0.001638142852500863, -0.003090213329823024, -0.005092926974060729, -0.007262597661114692, -0.008809825084618847, -0.008782215250663696, -0.006580595749872409, -0.00245131374472136] + [0.0] * 32 + [0.00245131374472136, 0.006580595749872409, 0.008782215250663696, 0.008809825084618847, 0.007262597661114692, 0.005092926974060729, 0.003090213329823024, 0.001638142852500863, 0.0007632554149722213, 0.0003138196197111826],
        },
        "q2_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006284517393142791, -0.0015284869490371185, -0.00328052696592678, -0.006188427427726713, -0.010199039875182862, -0.014543998671172639, -0.017642459393006495, -0.017587168241397614, -0.013178229100327028, -0.004908974103954795] + [0.0] * 32 + [0.004908974103954795, 0.013178229100327028, 0.017587168241397614, 0.017642459393006495, 0.014543998671172639, 0.010199039875182862, 0.006188427427726713, 0.00328052696592678, 0.0015284869490371185, 0.0006284517393142791],
        },
        "q2_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0017221707040954192, 0.004681345330447098, 0.011387023542088086, 0.024785336274866496, 0.04827524318154477, 0.08413935575233286, 0.13122571630483457, 0.18314024016584937, 0.22871448179981746, 0.25559279470870994] + [0.25916746124544393] * 32 + [0.25559279470870994, 0.22871448179981746, 0.18314024016584937, 0.13122571630483457, 0.08413935575233286, 0.04827524318154477, 0.024785336274866496, 0.011387023542088086, 0.004681345330447098, 0.0017221707040954192],
        },
        "q2_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003127532136030457, -0.000760661758663084, -0.0016325761975367295, -0.0030797123217171495, -0.005075620444792635, -0.007237918265626666, -0.008779887978422295, -0.008752371966821531, -0.0065582338991082584, -0.0024429838131742607] + [0.0] * 32 + [0.0024429838131742607, 0.0065582338991082584, 0.008752371966821531, 0.008779887978422295, 0.007237918265626666, 0.005075620444792635, 0.0030797123217171495, 0.0016325761975367295, 0.000760661758663084, 0.0003127532136030457],
        },
        "q2_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008570497754792741, 0.0023297028307702155, 0.005666828466490438, 0.01233458845806477, 0.024024497822172863, 0.04187251344191499, 0.0653053558678664, 0.09114096607386311, 0.11382129240106464, 0.1271974646870331] + [0.1289764214103333] * 32 + [0.1271974646870331, 0.11382129240106464, 0.09114096607386311, 0.0653053558678664, 0.04187251344191499, 0.024024497822172863, 0.01233458845806477, 0.005666828466490438, 0.0023297028307702155, 0.0008570497754792741],
        },
        "q2_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008400127900512386, -0.002043034502567416, -0.004384878642381167, -0.008271690353290131, -0.013632429358448805, -0.019440068565334388, -0.0235815904563419, -0.02350768617440165, -0.017614528375048785, -0.006561523782003884] + [0.0] * 32 + [0.006561523782003884, 0.017614528375048785, 0.02350768617440165, 0.0235815904563419, 0.019440068565334388, 0.013632429358448805, 0.008271690353290131, 0.004384878642381167, 0.002043034502567416, 0.0008400127900512386],
        },
        "q2_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0023019196663695667, 0.006257266399664901, 0.015220334064800986, 0.03312903469616625, 0.06452654862500447, 0.11246390224927966, 0.1754013445805286, 0.24479229587339238, 0.30570858184181127, 0.3416351696862567] + [0.34641320660330166] * 32 + [0.3416351696862567, 0.30570858184181127, 0.24479229587339238, 0.1754013445805286, 0.11246390224927966, 0.06452654862500447, 0.03312903469616625, 0.015220334064800986, 0.006257266399664901, 0.0023019196663695667],
        },
        "q2_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0023019196663695667, 0.006257266399664901, 0.015220334064800986, 0.03312903469616625, 0.06452654862500447, 0.11246390224927966, 0.1754013445805286, 0.24479229587339238, 0.30570858184181127, 0.3416351696862567] + [0.34641320660330166] * 32 + [0.3416351696862567, 0.30570858184181127, 0.24479229587339238, 0.1754013445805286, 0.11246390224927966, 0.06452654862500447, 0.03312903469616625, 0.015220334064800986, 0.006257266399664901, 0.0023019196663695667],
        },
        "q2_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008400127900512386, 0.002043034502567416, 0.004384878642381167, 0.008271690353290131, 0.013632429358448805, 0.019440068565334388, 0.0235815904563419, 0.02350768617440165, 0.017614528375048785, 0.006561523782003884] + [0.0] * 32 + [-0.006561523782003884, -0.017614528375048785, -0.02350768617440165, -0.0235815904563419, -0.019440068565334388, -0.013632429358448805, -0.008271690353290131, -0.004384878642381167, -0.002043034502567416, -0.0008400127900512386],
        },
        "q2_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003127532136030457, 0.000760661758663084, 0.0016325761975367295, 0.0030797123217171495, 0.005075620444792635, 0.007237918265626666, 0.008779887978422295, 0.008752371966821531, 0.0065582338991082584, 0.0024429838131742607] + [0.0] * 32 + [-0.0024429838131742607, -0.0065582338991082584, -0.008752371966821531, -0.008779887978422295, -0.007237918265626666, -0.005075620444792635, -0.0030797123217171495, -0.0016325761975367295, -0.000760661758663084, -0.0003127532136030457],
        },
        "q2_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008570497754792741, -0.0023297028307702155, -0.005666828466490438, -0.01233458845806477, -0.024024497822172863, -0.04187251344191499, -0.0653053558678664, -0.09114096607386311, -0.11382129240106464, -0.1271974646870331] + [-0.1289764214103333] * 32 + [-0.1271974646870331, -0.11382129240106464, -0.09114096607386311, -0.0653053558678664, -0.04187251344191499, -0.024024497822172863, -0.01233458845806477, -0.005666828466490438, -0.0023297028307702155, -0.0008570497754792741],
        },
        "q3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.001311080999574648+0j), (0.0035638876567816863+0j), (0.00866889105257577+0j), (0.01886896773982359+0j), (0.03675173078641692+0j), (0.06405492230300033+0j), (0.09990156196113596+0j), (0.1394238611584692+0j), (0.17411933131960183+0j), (0.19458167298623746+0j)] + [(0.19730305093383702+0j)] * 32 + [(0.19458167298623746+0j), (0.17411933131960183+0j), (0.1394238611584692+0j), (0.09990156196113596+0j), (0.06405492230300033+0j), (0.03675173078641692+0j), (0.01886896773982359+0j), (0.00866889105257577+0j), (0.0035638876567816863+0j), (0.001311080999574648+0j)],
        },
        "q3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.001063587408694751+0j), (0.0028911303260327854+0j), (0.0070324589967038255+0j), (0.01530706074579276+0j), (0.029814083283072335+0j), (0.05196323404007412+0j), (0.08104308082054011+0j), (0.11310473056040195+0j), (0.14125071483909798+0j), (0.15785036730611132+0j)] + [(0.16005802901450727+0j)] * 32 + [(0.15785036730611132+0j), (0.14125071483909798+0j), (0.11310473056040195+0j), (0.08104308082054011+0j), (0.05196323404007412+0j), (0.029814083283072335+0j), (0.01530706074579276+0j), (0.0070324589967038255+0j), (0.0028911303260327854+0j), (0.001063587408694751+0j)],
        },
        "q3_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.001063587408694751+0j), (0.0028911303260327854+0j), (0.0070324589967038255+0j), (0.01530706074579276+0j), (0.029814083283072335+0j), (0.05196323404007412+0j), (0.08104308082054011+0j), (0.11310473056040195+0j), (0.14125071483909798+0j), (0.15785036730611132+0j)] + [(0.16005802901450727+0j)] * 32 + [(0.15785036730611132+0j), (0.14125071483909798+0j), (0.11310473056040195+0j), (0.08104308082054011+0j), (0.05196323404007412+0j), (0.029814083283072335+0j), (0.01530706074579276+0j), (0.0070324589967038255+0j), (0.0028911303260327854+0j), (0.001063587408694751+0j)],
        },
        "q3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006509372807104426+0j), (0.0017694309816217407+0j), (0.004304008959301125+0j), (0.009368234727189726+0j), (0.018246829682737997+0j), (0.031802563650576134+0j), (0.04960002555357382+0j), (0.06922241194715517+0j), (0.08644833086977327+0j), (0.09660765820787753+0j)] + [(0.09795879239529275+0j)] * 32 + [(0.09660765820787753+0j), (0.08644833086977327+0j), (0.06922241194715517+0j), (0.04960002555357382+0j), (0.031802563650576134+0j), (0.018246829682737997+0j), (0.009368234727189726+0j), (0.004304008959301125+0j), (0.0017694309816217407+0j), (0.0006509372807104426+0j)],
        },
        "q3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0006509372807104426+0j), (-0.0017694309816217407+0j), (-0.004304008959301125+0j), (-0.009368234727189726+0j), (-0.018246829682737997+0j), (-0.031802563650576134+0j), (-0.04960002555357382+0j), (-0.06922241194715517+0j), (-0.08644833086977327+0j), (-0.09660765820787753+0j)] + [(-0.09795879239529275+0j)] * 32 + [(-0.09660765820787753+0j), (-0.08644833086977327+0j), (-0.06922241194715517+0j), (-0.04960002555357382+0j), (-0.031802563650576134+0j), (-0.018246829682737997+0j), (-0.009368234727189726+0j), (-0.004304008959301125+0j), (-0.0017694309816217407+0j), (-0.0006509372807104426+0j)],
        },
        "q3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.001309908128409933+0j), (0.003560699462407518+0j), (0.008661136007426828+0j), (0.01885208787643059+0j), (0.036718853301878025+0j), (0.06399761983934506+0j), (0.09981219169234844+0j), (0.13929913490091606+0j), (0.17396356707392177+0j), (0.1944076034714618+0j)] + [(0.19712654691980153+0j)] * 32 + [(0.1944076034714618+0j), (0.17396356707392177+0j), (0.13929913490091606+0j), (0.09981219169234844+0j), (0.06399761983934506+0j), (0.036718853301878025+0j), (0.01885208787643059+0j), (0.008661136007426828+0j), (0.003560699462407518+0j), (0.001309908128409933+0j)],
        },
        "q3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.000650507994801753+0j), (0.001768264061536936+0j), (0.004301170513183727+0j), (0.009362056480411034+0j), (0.018234796101173102+0j), (0.03178159021298089+0j), (0.049567314887474685+0j), (0.06917676053511437+0j), (0.08639131915547779+0j), (0.09654394653001067+0j)] + [(0.09789418965943214+0j)] * 32 + [(0.09654394653001067+0j), (0.08639131915547779+0j), (0.06917676053511437+0j), (0.049567314887474685+0j), (0.03178159021298089+0j), (0.018234796101173102+0j), (0.009362056480411034+0j), (0.004301170513183727+0j), (0.001768264061536936+0j), (0.000650507994801753+0j)],
        },
        "q3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.000650507994801753+0j), (-0.001768264061536936+0j), (-0.004301170513183727+0j), (-0.009362056480411034+0j), (-0.018234796101173102+0j), (-0.03178159021298089+0j), (-0.049567314887474685+0j), (-0.06917676053511437+0j), (-0.08639131915547779+0j), (-0.09654394653001067+0j)] + [(-0.09789418965943214+0j)] * 32 + [(-0.09654394653001067+0j), (-0.08639131915547779+0j), (-0.06917676053511437+0j), (-0.049567314887474685+0j), (-0.03178159021298089+0j), (-0.018234796101173102+0j), (-0.009362056480411034+0j), (-0.004301170513183727+0j), (-0.001768264061536936+0j), (-0.000650507994801753+0j)],
        },
        "q3_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.000311223896625865+0j), (0.00032577165523137104+0j), (0.0003409211562887489+0j), (0.0003566932662804085+0j), (0.00037310938088465655+0j), (0.0003901914293614473+0j), (0.0004079618785141323+0j), (0.0004264437362021095+0j), (0.0004456605543788675+0j), (0.0004656364316295382+0j), (0.0004863960151817112+0j), (0.0005079645023629436+0j), (0.0005303676414781189+0j), (0.0005536317320795551+0j), (0.0005777836246025627+0j), (0.0006028507193389735+0j), (0.0006288609647210594+0j), (0.0006558428548881647+0j), (0.0006838254265083703+0j), (0.0007128382548275099+0j), (0.000742911448917959+0j), (0.0007740756460997302+0j), (0.0008063620055066135+0j), (0.0008398022007703349+0j), (0.0008744284117960341+0j), (0.0009102733156027127+0j), (0.0009473700762027662+0j), (0.0009857523334951988+0j), (0.0010254541911477047+0j), (0.0010665102034434334+0j), (0.001108955361068983+0j), (0.0011528250758209412+0j), (0.001198155164209159+0j), (0.0012449818299358857+0j), (0.0012933416452308927+0j), (0.001343271531023825+0j), (0.001394808735936162+0j), (0.001447990814076442+0j), (0.0015028556016237094+0j), (0.0015594411921855662+0j), (0.0016177859109186856+0j), (0.001677928287401205+0j), (0.0017399070272480768+0j), (0.0018037609824621485+0j), (0.0018695291205155869+0j), (0.0019372504921580757+0j), (0.0020069641979502434+0j), (0.0020787093535227347+0j), (0.002152525053563493+0j), (0.0022284503345379554+0j), (0.0023065241361491322+0j), (0.0023867852615468304+0j), (0.002469272336297659+0j), (0.0025540237661298947+0j), (0.0026410776934697776+0j), (0.0027304719527883443+0j), (0.0028222440247805333+0j), (0.0029164309894009134+0j), (0.0030130694777831214+0j), (0.0031121956230727955+0j), (0.003213845010206586+0j), (0.003318052624672616+0j), (0.0034248528002906085+0j), (0.003534279166052743+0j), (0.0036463645920691633+0j), (0.0037611411346649593+0j), (0.0038786399806783195+0j), (0.003998891391012432+0j), (0.00412192464349661+0j), (0.004247767975114953+0j), (0.0043764485236637415+0j), (0.004507992268901533+0j), (0.0046424239732587745+0j), (0.00477976712217646+0j), (0.004920043864146036+0j), (0.0050632749505254955+0j), (0.005209479675209109+0j), (0.005358675814230768+0j), (0.005510879565383436+0j), (0.005666105487939465+0j), (0.005824366442558891+0j), (0.005985673531474939+0j), (0.006150036039048107+0j), (0.0063174613727820786+0j), (0.006487955004896619+0j), (0.006661520414554313+0j), (0.006838159030839568+0j), (0.0070178701765897375+0j), (0.007200651013179588+0j), (0.007386496486361374+0j), (0.007575399273263843+0j), (0.0077673497306542764+0j), (0.007962335844568335+0j), (0.008160343181412896+0j), (0.008361354840647449+0j), (0.008565351409149572+0j), (0.00877231091737005+0j), (0.008982208797382775+0j), (0.009195017842934177+0j), (0.009410708171596123+0j), (0.009629247189125369+0j), (0.009850599556131497+0j), (0.010074727157153912+0j), (0.010301589072246911+0j), (0.010531141551170058+0j), (0.010763337990279074+0j), (0.010998128912210215+0j), (0.011235461948448692+0j), (0.011475281824868948+0j), (0.011717530350331776+0j), (0.011962146408420072+0j), (0.01220906595239174+0j), (0.01245822200342467+0j), (0.012709544652224925+0j), (0.01296296106406537+0j), (0.013218395487317664+0j), (0.013475769265536262+0j), (0.013735000853148428+0j), (0.013996005834799456+0j), (0.014258696948397421+0j), (0.01452298411189651+0j), (0.014788774453852823+0j), (0.015055972347780855+0j), (0.015324479450333491+0j), (0.01559419474332229+0j), (0.015865014579589134+0j), (0.01613683273273416+0j), (0.016409540450698784+0j), (0.01668302651319626+0j), (0.016957177292976036+0j), (0.017231876820901517+0j), (0.017507006854814478+0j), (0.017782446952152715+0j), (0.018058074546280917+0j), (0.018333765026488123+0j), (0.01860939182159837+0j), (0.018884826487134514+0j), (0.019159938795968574+0j), (0.01943459683238516+0j), (0.019708667089478053+0j), (0.019982014569793396+0j), (0.02025450288912642+0j), (0.020525994383372263+0j), (0.02079635021832506+0j), (0.021065430502313257+0j), (0.021333094401553034+0j), (0.021599200258095815+0j), (0.02186360571023976+0j), (0.022126167815269906+0j), (0.02238674317438578+0j), (0.02264518805967022+0j), (0.022901358542948013+0j), (0.02315511062637814+0j), (0.023406300374618723+0j), (0.0236547840483995+0j), (0.02390041823933236+0j), (0.02414306000578686+0j), (0.02438256700965382+0j), (0.02461879765381692+0j), (0.024851611220149287+0j), (0.02508086800784923+0j), (0.025306429471927034+0j), (0.025528158361652602+0j), (0.025745918858772126+0j), (0.025959576715300386+0j), (0.026168999390694562+0j), (0.026374056188214413+0j), (0.026574618390273603+0j), (0.026770559392586914+0j), (0.026961754836918376+0j), (0.027148082742236273+0j), (0.02732942363408195+0j), (0.027505660671960867+0j), (0.027676679774566282+0j), (0.027842369742647952+0j), (0.028002622379341046+0j), (0.028157332607773172+0j), (0.02830639858577082+0j), (0.02844972181749017+0j), (0.02858720726180099+0j), (0.028718763437256954+0j), (0.028844302523490076+0j), (0.028963740458872005+0j), (0.029076997034290324+0j), (0.029183995982893302+0j), (0.029284665065662692+0j), (0.02937893615268013+0j), (0.02946674529995916+0j), (0.029548032821721682+0j), (0.029622743358004387+0j), (0.029690825937488025+0j), (0.0297522340354497+0j), (0.029806925626745914+0j), (0.029854863233741962+0j), (0.02989601396911107+0j), (0.02993034957343494+0j), (0.029957846447545455+0j), (0.0299784856795558+0j), (0.029992253066537564+0j), (0.029999139130809132+0j)] + [(0.03+0j)] * 3200 + [(0.029999139130809132+0j), (0.029992253066537564+0j), (0.0299784856795558+0j), (0.029957846447545455+0j), (0.02993034957343494+0j), (0.02989601396911107+0j), (0.029854863233741962+0j), (0.029806925626745914+0j), (0.0297522340354497+0j), (0.029690825937488025+0j), (0.029622743358004387+0j), (0.029548032821721682+0j), (0.02946674529995916+0j), (0.02937893615268013+0j), (0.029284665065662692+0j), (0.029183995982893302+0j), (0.029076997034290324+0j), (0.028963740458872005+0j), (0.028844302523490076+0j), (0.028718763437256954+0j), (0.02858720726180099+0j), (0.02844972181749017+0j), (0.02830639858577082+0j), (0.028157332607773172+0j), (0.028002622379341046+0j), (0.027842369742647952+0j), (0.027676679774566282+0j), (0.027505660671960867+0j), (0.02732942363408195+0j), (0.027148082742236273+0j), (0.026961754836918376+0j), (0.026770559392586914+0j), (0.026574618390273603+0j), (0.026374056188214413+0j), (0.026168999390694562+0j), (0.025959576715300386+0j), (0.025745918858772126+0j), (0.025528158361652602+0j), (0.025306429471927034+0j), (0.02508086800784923+0j), (0.024851611220149287+0j), (0.02461879765381692+0j), (0.02438256700965382+0j), (0.02414306000578686+0j), (0.02390041823933236+0j), (0.0236547840483995+0j), (0.023406300374618723+0j), (0.02315511062637814+0j), (0.022901358542948013+0j), (0.02264518805967022+0j), (0.02238674317438578+0j), (0.022126167815269906+0j), (0.02186360571023976+0j), (0.021599200258095815+0j), (0.021333094401553034+0j), (0.021065430502313257+0j), (0.02079635021832506+0j), (0.020525994383372263+0j), (0.02025450288912642+0j), (0.019982014569793396+0j), (0.019708667089478053+0j), (0.01943459683238516+0j), (0.019159938795968574+0j), (0.018884826487134514+0j), (0.01860939182159837+0j), (0.018333765026488123+0j), (0.018058074546280917+0j), (0.017782446952152715+0j), (0.017507006854814478+0j), (0.017231876820901517+0j), (0.016957177292976036+0j), (0.01668302651319626+0j), (0.016409540450698784+0j), (0.01613683273273416+0j), (0.015865014579589134+0j), (0.01559419474332229+0j), (0.015324479450333491+0j), (0.015055972347780855+0j), (0.014788774453852823+0j), (0.01452298411189651+0j), (0.014258696948397421+0j), (0.013996005834799456+0j), (0.013735000853148428+0j), (0.013475769265536262+0j), (0.013218395487317664+0j), (0.01296296106406537+0j), (0.012709544652224925+0j), (0.01245822200342467+0j), (0.01220906595239174+0j), (0.011962146408420072+0j), (0.011717530350331776+0j), (0.011475281824868948+0j), (0.011235461948448692+0j), (0.010998128912210215+0j), (0.010763337990279074+0j), (0.010531141551170058+0j), (0.010301589072246911+0j), (0.010074727157153912+0j), (0.009850599556131497+0j), (0.009629247189125369+0j), (0.009410708171596123+0j), (0.009195017842934177+0j), (0.008982208797382775+0j), (0.00877231091737005+0j), (0.008565351409149572+0j), (0.008361354840647449+0j), (0.008160343181412896+0j), (0.007962335844568335+0j), (0.0077673497306542764+0j), (0.007575399273263843+0j), (0.007386496486361374+0j), (0.007200651013179588+0j), (0.0070178701765897375+0j), (0.006838159030839568+0j), (0.006661520414554313+0j), (0.006487955004896619+0j), (0.0063174613727820786+0j), (0.006150036039048107+0j), (0.005985673531474939+0j), (0.005824366442558891+0j), (0.005666105487939465+0j), (0.005510879565383436+0j), (0.005358675814230768+0j), (0.005209479675209109+0j), (0.0050632749505254955+0j), (0.004920043864146036+0j), (0.00477976712217646+0j), (0.0046424239732587745+0j), (0.004507992268901533+0j), (0.0043764485236637415+0j), (0.004247767975114953+0j), (0.00412192464349661+0j), (0.003998891391012432+0j), (0.0038786399806783195+0j), (0.0037611411346649593+0j), (0.0036463645920691633+0j), (0.003534279166052743+0j), (0.0034248528002906085+0j), (0.003318052624672616+0j), (0.003213845010206586+0j), (0.0031121956230727955+0j), (0.0030130694777831214+0j), (0.0029164309894009134+0j), (0.0028222440247805333+0j), (0.0027304719527883443+0j), (0.0026410776934697776+0j), (0.0025540237661298947+0j), (0.002469272336297659+0j), (0.0023867852615468304+0j), (0.0023065241361491322+0j), (0.0022284503345379554+0j), (0.002152525053563493+0j), (0.0020787093535227347+0j), (0.0020069641979502434+0j), (0.0019372504921580757+0j), (0.0018695291205155869+0j), (0.0018037609824621485+0j), (0.0017399070272480768+0j), (0.001677928287401205+0j), (0.0016177859109186856+0j), (0.0015594411921855662+0j), (0.0015028556016237094+0j), (0.001447990814076442+0j), (0.001394808735936162+0j), (0.001343271531023825+0j), (0.0012933416452308927+0j), (0.0012449818299358857+0j), (0.001198155164209159+0j), (0.0011528250758209412+0j), (0.001108955361068983+0j), (0.0010665102034434334+0j), (0.0010254541911477047+0j), (0.0009857523334951988+0j), (0.0009473700762027662+0j), (0.0009102733156027127+0j), (0.0008744284117960341+0j), (0.0008398022007703349+0j), (0.0008063620055066135+0j), (0.0007740756460997302+0j), (0.000742911448917959+0j), (0.0007128382548275099+0j), (0.0006838254265083703+0j), (0.0006558428548881647+0j), (0.0006288609647210594+0j), (0.0006028507193389735+0j), (0.0005777836246025627+0j), (0.0005536317320795551+0j), (0.0005303676414781189+0j), (0.0005079645023629436+0j), (0.0004863960151817112+0j), (0.0004656364316295382+0j), (0.0004456605543788675+0j), (0.0004264437362021095+0j), (0.0004079618785141323+0j), (0.0003901914293614473+0j), (0.00037310938088465655+0j), (0.0003566932662804085+0j), (0.0003409211562887489+0j), (0.00032577165523137104+0j), (0.000311223896625865+0j)],
        },
        "q3_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001311080999574648, 0.0035638876567816863, 0.00866889105257577, 0.01886896773982359, 0.03675173078641692, 0.06405492230300033, 0.09990156196113596, 0.1394238611584692, 0.17411933131960183, 0.19458167298623746] + [0.19730305093383702] * 32 + [0.19458167298623746, 0.17411933131960183, 0.1394238611584692, 0.09990156196113596, 0.06405492230300033, 0.03675173078641692, 0.01886896773982359, 0.00866889105257577, 0.0035638876567816863, 0.001311080999574648],
        },
        "q3_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0030801133862301787, -0.00749128822134264, -0.016078235430878638, -0.03033018602296031, -0.049986653359449684, -0.07128179014234601, -0.08646769822248304, -0.08619671000563695, -0.0645879982813234, -0.024059439897081876] + [0.0] * 32 + [0.024059439897081876, 0.0645879982813234, 0.08619671000563695, 0.08646769822248304, 0.07128179014234601, 0.049986653359449684, 0.03033018602296031, 0.016078235430878638, 0.00749128822134264, 0.0030801133862301787],
        },
        "q3_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006509372807104426, 0.0017694309816217407, 0.004304008959301125, 0.009368234727189726, 0.018246829682737997, 0.031802563650576134, 0.04960002555357382, 0.06922241194715517, 0.08644833086977327, 0.09660765820787753] + [0.09795879239529275] * 32 + [0.09660765820787753, 0.08644833086977327, 0.06922241194715517, 0.04960002555357382, 0.031802563650576134, 0.018246829682737997, 0.009368234727189726, 0.004304008959301125, 0.0017694309816217407, 0.0006509372807104426],
        },
        "q3_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0015292423828603817, -0.0037193421195189135, -0.007982666862988541, -0.01505860341171359, -0.02481782301793101, -0.03539062396181824, -0.04293026012008012, -0.04279571745411547, -0.03206723000441259, -0.011945247003887436] + [0.0] * 32 + [0.011945247003887436, 0.03206723000441259, 0.04279571745411547, 0.04293026012008012, 0.03539062396181824, 0.02481782301793101, 0.01505860341171359, 0.007982666862988541, 0.0037193421195189135, 0.0015292423828603817],
        },
        "q3_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006509372807104426, -0.0017694309816217407, -0.004304008959301125, -0.009368234727189726, -0.018246829682737997, -0.031802563650576134, -0.04960002555357382, -0.06922241194715517, -0.08644833086977327, -0.09660765820787753] + [-0.09795879239529275] * 32 + [-0.09660765820787753, -0.08644833086977327, -0.06922241194715517, -0.04960002555357382, -0.031802563650576134, -0.018246829682737997, -0.009368234727189726, -0.004304008959301125, -0.0017694309816217407, -0.0006509372807104426],
        },
        "q3_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0015292423828603817, 0.0037193421195189135, 0.007982666862988541, 0.01505860341171359, 0.02481782301793101, 0.03539062396181824, 0.04293026012008012, 0.04279571745411547, 0.03206723000441259, 0.011945247003887436] + [0.0] * 32 + [-0.011945247003887436, -0.03206723000441259, -0.04279571745411547, -0.04293026012008012, -0.03539062396181824, -0.02481782301793101, -0.01505860341171359, -0.007982666862988541, -0.0037193421195189135, -0.0015292423828603817],
        },
        "q3_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.003077357968238511, 0.007484586640018349, 0.016063852109998777, 0.030303053145114993, 0.04994193613422491, 0.07121802264342385, 0.08639034566382547, 0.08611959986851216, 0.06453021893680129, 0.024037916723987585] + [0.0] * 32 + [-0.024037916723987585, -0.06453021893680129, -0.08611959986851216, -0.08639034566382547, -0.07121802264342385, -0.04994193613422491, -0.030303053145114993, -0.016063852109998777, -0.007484586640018349, -0.003077357968238511],
        },
        "q3_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001309908128409933, 0.003560699462407518, 0.008661136007426828, 0.01885208787643059, 0.036718853301878025, 0.06399761983934506, 0.09981219169234844, 0.13929913490091606, 0.17396356707392177, 0.1944076034714618] + [0.19712654691980153] * 32 + [0.1944076034714618, 0.17396356707392177, 0.13929913490091606, 0.09981219169234844, 0.06399761983934506, 0.036718853301878025, 0.01885208787643059, 0.008661136007426828, 0.003560699462407518, 0.001309908128409933],
        },
        "q3_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0015282338644894316, 0.003716889254690273, 0.00797740238283109, 0.015048672429972708, 0.024801455939225173, 0.03536728423828917, 0.042901948090224, 0.042767494153653614, 0.032046082022295815, 0.011937369246127134] + [0.0] * 32 + [-0.011937369246127134, -0.032046082022295815, -0.042767494153653614, -0.042901948090224, -0.03536728423828917, -0.024801455939225173, -0.015048672429972708, -0.00797740238283109, -0.003716889254690273, -0.0015282338644894316],
        },
        "q3_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000650507994801753, 0.001768264061536936, 0.004301170513183727, 0.009362056480411034, 0.018234796101173102, 0.03178159021298089, 0.049567314887474685, 0.06917676053511437, 0.08639131915547779, 0.09654394653001067] + [0.09789418965943214] * 32 + [0.09654394653001067, 0.08639131915547779, 0.06917676053511437, 0.049567314887474685, 0.03178159021298089, 0.018234796101173102, 0.009362056480411034, 0.004301170513183727, 0.001768264061536936, 0.000650507994801753],
        },
        "q3_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0024986784310118055, 0.006077152997952269, 0.01304313674277964, 0.024604737592761845, 0.04055064113746455, 0.0578258814590534, 0.07014513605039417, 0.06992530245091737, 0.05239568092825722, 0.019517724185680613] + [0.0] * 32 + [-0.019517724185680613, -0.05239568092825722, -0.06992530245091737, -0.07014513605039417, -0.0578258814590534, -0.04055064113746455, -0.024604737592761845, -0.01304313674277964, -0.006077152997952269, -0.0024986784310118055],
        },
        "q3_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001063587408694751, 0.0028911303260327854, 0.0070324589967038255, 0.01530706074579276, 0.029814083283072335, 0.05196323404007412, 0.08104308082054011, 0.11310473056040195, 0.14125071483909798, 0.15785036730611132] + [0.16005802901450727] * 32 + [0.15785036730611132, 0.14125071483909798, 0.11310473056040195, 0.08104308082054011, 0.05196323404007412, 0.029814083283072335, 0.01530706074579276, 0.0070324589967038255, 0.0028911303260327854, 0.001063587408694751],
        },
        "q3_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.001063587408694751, 0.0028911303260327854, 0.0070324589967038255, 0.01530706074579276, 0.029814083283072335, 0.05196323404007412, 0.08104308082054011, 0.11310473056040195, 0.14125071483909798, 0.15785036730611132] + [0.16005802901450727] * 32 + [0.15785036730611132, 0.14125071483909798, 0.11310473056040195, 0.08104308082054011, 0.05196323404007412, 0.029814083283072335, 0.01530706074579276, 0.0070324589967038255, 0.0028911303260327854, 0.001063587408694751],
        },
        "q3_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0024986784310118055, -0.006077152997952269, -0.01304313674277964, -0.024604737592761845, -0.04055064113746455, -0.0578258814590534, -0.07014513605039417, -0.06992530245091737, -0.05239568092825722, -0.019517724185680613] + [0.0] * 32 + [0.019517724185680613, 0.05239568092825722, 0.06992530245091737, 0.07014513605039417, 0.0578258814590534, 0.04055064113746455, 0.024604737592761845, 0.01304313674277964, 0.006077152997952269, 0.0024986784310118055],
        },
        "q3_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0015282338644894316, -0.003716889254690273, -0.00797740238283109, -0.015048672429972708, -0.024801455939225173, -0.03536728423828917, -0.042901948090224, -0.042767494153653614, -0.032046082022295815, -0.011937369246127134] + [0.0] * 32 + [0.011937369246127134, 0.032046082022295815, 0.042767494153653614, 0.042901948090224, 0.03536728423828917, 0.024801455939225173, 0.015048672429972708, 0.00797740238283109, 0.003716889254690273, 0.0015282338644894316],
        },
        "q3_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000650507994801753, -0.001768264061536936, -0.004301170513183727, -0.009362056480411034, -0.018234796101173102, -0.03178159021298089, -0.049567314887474685, -0.06917676053511437, -0.08639131915547779, -0.09654394653001067] + [-0.09789418965943214] * 32 + [-0.09654394653001067, -0.08639131915547779, -0.06917676053511437, -0.049567314887474685, -0.03178159021298089, -0.018234796101173102, -0.009362056480411034, -0.004301170513183727, -0.001768264061536936, -0.000650507994801753],
        },
        "q4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0007285172954878752+0j), (0.0019803153260428198+0j), (0.0048169694065816285+0j), (0.010484759790527026+0j), (0.02042152355629078+0j), (0.035592857172064334+0j), (0.055511456392513564+0j), (0.07747247827601657+0j), (0.0967514168737607+0j), (0.10812155328422088+0j)] + [(0.10963371836252556+0j)] * 32 + [(0.10812155328422088+0j), (0.0967514168737607+0j), (0.07747247827601657+0j), (0.055511456392513564+0j), (0.035592857172064334+0j), (0.02042152355629078+0j), (0.010484759790527026+0j), (0.0048169694065816285+0j), (0.0019803153260428198+0j), (0.0007285172954878752+0j)],
        },
        "q4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q4_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0003639874941886334+0j), (0.0009894205912393044+0j), (0.002406691831126384+0j), (0.005238477476046673+0j), (0.010203160903394286+0j), (0.01778318095303098+0j), (0.027735066876540457+0j), (0.03870740394349351+0j), (0.04833969763682312+0j), (0.054020533886365844+0j)] + [(0.05477605359888424+0j)] * 32 + [(0.054020533886365844+0j), (0.04833969763682312+0j), (0.03870740394349351+0j), (0.027735066876540457+0j), (0.01778318095303098+0j), (0.010203160903394286+0j), (0.005238477476046673+0j), (0.002406691831126384+0j), (0.0009894205912393044+0j), (0.0003639874941886334+0j)],
        },
        "q4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0003639874941886334+0j), (-0.0009894205912393044+0j), (-0.002406691831126384+0j), (-0.005238477476046673+0j), (-0.010203160903394286+0j), (-0.01778318095303098+0j), (-0.027735066876540457+0j), (-0.03870740394349351+0j), (-0.04833969763682312+0j), (-0.054020533886365844+0j)] + [(-0.05477605359888424+0j)] * 32 + [(-0.054020533886365844+0j), (-0.04833969763682312+0j), (-0.03870740394349351+0j), (-0.027735066876540457+0j), (-0.01778318095303098+0j), (-0.010203160903394286+0j), (-0.005238477476046673+0j), (-0.002406691831126384+0j), (-0.0009894205912393044+0j), (-0.0003639874941886334+0j)],
        },
        "q4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0007303611396639445+0j), (0.0019853274141611392+0j), (0.0048291609372997585+0j), (0.010511296241201545+0j), (0.02047320950459831+0j), (0.035682941076472435+0j), (0.0556519533665846+0j), (0.0776685575987171+0j), (0.09699629031414987+0j), (0.1083952040232842+0j)] + [(0.1099111963226997+0j)] * 32 + [(0.1083952040232842+0j), (0.09699629031414987+0j), (0.0776685575987171+0j), (0.0556519533665846+0j), (0.035682941076472435+0j), (0.02047320950459831+0j), (0.010511296241201545+0j), (0.0048291609372997585+0j), (0.0019853274141611392+0j), (0.0007303611396639445+0j)],
        },
        "q4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00036409595561075507+0j), (0.0009897154199521466+0j), (0.002407408979992156+0j), (0.005240038443733408+0j), (0.010206201253294727+0j), (0.017788480006231455+0j), (0.027743331404426988+0j), (0.038718938021299415+0j), (0.04835410195684601+0j), (0.05403663098866368+0j)] + [(0.05479237583183565+0j)] * 32 + [(0.05403663098866368+0j), (0.04835410195684601+0j), (0.038718938021299415+0j), (0.027743331404426988+0j), (0.017788480006231455+0j), (0.010206201253294727+0j), (0.005240038443733408+0j), (0.002407408979992156+0j), (0.0009897154199521466+0j), (0.00036409595561075507+0j)],
        },
        "q4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00036409595561075507+0j), (-0.0009897154199521466+0j), (-0.002407408979992156+0j), (-0.005240038443733408+0j), (-0.010206201253294727+0j), (-0.017788480006231455+0j), (-0.027743331404426988+0j), (-0.038718938021299415+0j), (-0.04835410195684601+0j), (-0.05403663098866368+0j)] + [(-0.05479237583183565+0j)] * 32 + [(-0.05403663098866368+0j), (-0.04835410195684601+0j), (-0.038718938021299415+0j), (-0.027743331404426988+0j), (-0.017788480006231455+0j), (-0.010206201253294727+0j), (-0.005240038443733408+0j), (-0.002407408979992156+0j), (-0.0009897154199521466+0j), (-0.00036409595561075507+0j)],
        },
        "q4_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0002074825977505767+0j), (0.00021718110348758075+0j), (0.000227280770859166+0j), (0.00023779551085360574+0j), (0.00024873958725643775+0j), (0.00026012761957429825+0j), (0.00027197458567608827+0j), (0.00028429582413473973+0j), (0.00029710703625257837+0j), (0.0003104242877530255+0j), (0.00032426401012114085+0j), (0.00033864300157529585+0j), (0.00035357842765207934+0j), (0.0003690878213863702+0j), (0.00038518908306837523+0j), (0.00040190047955931577+0j), (0.00041924064314737306+0j), (0.0004372285699254432+0j), (0.000455883617672247+0j), (0.0004752255032183401+0j), (0.0004952742992786395+0j), (0.0005160504307331536+0j), (0.0005375746703377424+0j), (0.00055986813384689+0j), (0.0005829522745306895+0j), (0.0006068488770684752+0j), (0.0006315800508018443+0j), (0.0006571682223301327+0j), (0.0006836361274318032+0j), (0.0007110068022956224+0j), (0.0007393035740459889+0j), (0.0007685500505472943+0j), (0.0007987701094727728+0j), (0.0008299878866239239+0j), (0.000862227763487262+0j), (0.0008955143540158835+0j), (0.0009298724906241083+0j), (0.0009653272093842949+0j), (0.0010019037344158065+0j), (0.0010396274614570445+0j), (0.0010785239406124573+0j), (0.0011186188582674702+0j), (0.0011599380181653847+0j), (0.0012025073216414327+0j), (0.0012463527470103915+0j), (0.0012915003281053841+0j), (0.0013379761319668292+0j), (0.0013858062356818235+0j), (0.001435016702375662+0j), (0.0014856335563586374+0j), (0.001537682757432755+0j), (0.001591190174364554+0j), (0.0016461815575317732+0j), (0.0017026825107532635+0j), (0.0017607184623131857+0j), (0.0018203146351922297+0j), (0.001881496016520356+0j), (0.0019442873262672763+0j), (0.002008712985188748+0j), (0.002074797082048531+0j), (0.0021425633401377245+0j), (0.0022120350831150775+0j), (0.0022832352001937394+0j), (0.0023561861107018293+0j), (0.0024309097280461093+0j), (0.0025074274231099737+0j), (0.00258575998711888+0j), (0.002665927594008288+0j), (0.002747949762331074+0j), (0.002831845316743303+0j), (0.0029176323491091616+0j), (0.003005328179267689+0j), (0.0030949493155058507+0j), (0.003186511414784307+0j), (0.0032800292427640244+0j), (0.0033755166336836644+0j), (0.0034729864501394066+0j), (0.003572450542820513+0j), (0.003673919710255625+0j), (0.003777403658626311+0j), (0.003882910961705928+0j), (0.003990449020983293+0j), (0.004100024026032072+0j), (0.004211640915188053+0j), (0.004325303336597747+0j), (0.0044410136097028765+0j), (0.00455877268722638+0j), (0.0046785801177264925+0j), (0.004800434008786394+0j), (0.004924330990907584+0j), (0.005050266182175896+0j), (0.005178233153769519+0j), (0.00530822389637889+0j), (0.005440228787608598+0j), (0.005574236560431633+0j), (0.005710234272766382+0j), (0.005848207278246701+0j), (0.005988139198255185+0j), (0.006130011895289452+0j), (0.00627380544773075+0j), (0.00641949812608358+0j), (0.0065670663707543325+0j), (0.006716484771435942+0j), (0.006867726048164609+0j), (0.007020761034113373+0j), (0.00717555866018605+0j), (0.007332085941473478+0j), (0.007490307965632463+0j), (0.007650187883245967+0j), (0.007811686900221186+0j), (0.00797476427228005+0j), (0.008139377301594496+0j), (0.008305481335616448+0j), (0.008473029768149952+0j), (0.008641974042710249+0j), (0.008812263658211777+0j), (0.008983846177024177+0j), (0.009156667235432287+0j), (0.009330670556532972+0j), (0.009505797965598282+0j), (0.009681989407931009+0j), (0.009859182969235217+0j), (0.010037314898520572+0j), (0.010216319633555664+0j), (0.010396129828881528+0j), (0.010576676386392758+0j), (0.010757888488489442+0j), (0.010939693633799192+0j), (0.011122017675464176+0j), (0.011304784861984028+0j), (0.011487917880601016+0j), (0.011671337903209655+0j), (0.011854964634768478+0j), (0.01203871636418728+0j), (0.012222510017658752+0j), (0.012406261214398915+0j), (0.012589884324756344+0j), (0.012773292530645719+0j), (0.012956397888256777+0j), (0.013139111392985372+0j), (0.013321343046528933+0j), (0.013503001926084283+0j), (0.013683996255581513+0j), (0.013864233478883378+0j), (0.014043620334875507+0j), (0.014222062934368694+0j), (0.014399466838730546+0j), (0.014575737140159844+0j), (0.014750778543513275+0j), (0.014924495449590524+0j), (0.01509679203978015+0j), (0.015267572361965345+0j), (0.015436740417585429+0j), (0.01560420024974582+0j), (0.015769856032266338+0j), (0.01593361215955491+0j), (0.016095373337191243+0j), (0.016255044673102553+0j), (0.016412531769211283+0j), (0.01656774081343286+0j), (0.01672057867189949+0j), (0.016870952981284694+0j), (0.01701877224110174+0j), (0.017163945905848087+0j), (0.01730638447686693+0j), (0.017445999593796377+0j), (0.01758270412547628+0j), (0.017716412260182408+0j), (0.017847039595057946+0j), (0.017974503224612255+0j), (0.01809872182815752+0j), (0.018219615756054637+0j), (0.018337107114640584+0j), (0.01845111984971086+0j), (0.018561579828431974+0j), (0.018668414919560703+0j), (0.018771555071848786+0j), (0.018870932390513885+0j), (0.018966481211660117+0j), (0.019058138174533997+0j), (0.019145842291504643+0j), (0.019229535015660056+0j), (0.019309160305914674+0j), (0.019384664689526886+0j), (0.01945599732192887+0j), (0.019523110043775133+0j), (0.01958595743512009+0j), (0.019644496866639445+0j), (0.01969868854781446+0j), (0.01974849557200293+0j), (0.019793883958325355+0j), (0.019834822690299805+0j), (0.019871283751163947+0j), (0.01990324215582798+0j), (0.019930675979407387+0j), (0.019953566382289963+0j), (0.019971897631696975+0j), (0.019985657119703872+0j), (0.019994835377691714+0j), (0.019999426087206094+0j)] + [(0.020000000000000004+0j)] * 3200 + [(0.019999426087206094+0j), (0.019994835377691714+0j), (0.019985657119703872+0j), (0.019971897631696975+0j), (0.019953566382289963+0j), (0.019930675979407387+0j), (0.01990324215582798+0j), (0.019871283751163947+0j), (0.019834822690299805+0j), (0.019793883958325355+0j), (0.01974849557200293+0j), (0.01969868854781446+0j), (0.019644496866639445+0j), (0.01958595743512009+0j), (0.019523110043775133+0j), (0.01945599732192887+0j), (0.019384664689526886+0j), (0.019309160305914674+0j), (0.019229535015660056+0j), (0.019145842291504643+0j), (0.019058138174533997+0j), (0.018966481211660117+0j), (0.018870932390513885+0j), (0.018771555071848786+0j), (0.018668414919560703+0j), (0.018561579828431974+0j), (0.01845111984971086+0j), (0.018337107114640584+0j), (0.018219615756054637+0j), (0.01809872182815752+0j), (0.017974503224612255+0j), (0.017847039595057946+0j), (0.017716412260182408+0j), (0.01758270412547628+0j), (0.017445999593796377+0j), (0.01730638447686693+0j), (0.017163945905848087+0j), (0.01701877224110174+0j), (0.016870952981284694+0j), (0.01672057867189949+0j), (0.01656774081343286+0j), (0.016412531769211283+0j), (0.016255044673102553+0j), (0.016095373337191243+0j), (0.01593361215955491+0j), (0.015769856032266338+0j), (0.01560420024974582+0j), (0.015436740417585429+0j), (0.015267572361965345+0j), (0.01509679203978015+0j), (0.014924495449590524+0j), (0.014750778543513275+0j), (0.014575737140159844+0j), (0.014399466838730546+0j), (0.014222062934368694+0j), (0.014043620334875507+0j), (0.013864233478883378+0j), (0.013683996255581513+0j), (0.013503001926084283+0j), (0.013321343046528933+0j), (0.013139111392985372+0j), (0.012956397888256777+0j), (0.012773292530645719+0j), (0.012589884324756344+0j), (0.012406261214398915+0j), (0.012222510017658752+0j), (0.01203871636418728+0j), (0.011854964634768478+0j), (0.011671337903209655+0j), (0.011487917880601016+0j), (0.011304784861984028+0j), (0.011122017675464176+0j), (0.010939693633799192+0j), (0.010757888488489442+0j), (0.010576676386392758+0j), (0.010396129828881528+0j), (0.010216319633555664+0j), (0.010037314898520572+0j), (0.009859182969235217+0j), (0.009681989407931009+0j), (0.009505797965598282+0j), (0.009330670556532972+0j), (0.009156667235432287+0j), (0.008983846177024177+0j), (0.008812263658211777+0j), (0.008641974042710249+0j), (0.008473029768149952+0j), (0.008305481335616448+0j), (0.008139377301594496+0j), (0.00797476427228005+0j), (0.007811686900221186+0j), (0.007650187883245967+0j), (0.007490307965632463+0j), (0.007332085941473478+0j), (0.00717555866018605+0j), (0.007020761034113373+0j), (0.006867726048164609+0j), (0.006716484771435942+0j), (0.0065670663707543325+0j), (0.00641949812608358+0j), (0.00627380544773075+0j), (0.006130011895289452+0j), (0.005988139198255185+0j), (0.005848207278246701+0j), (0.005710234272766382+0j), (0.005574236560431633+0j), (0.005440228787608598+0j), (0.00530822389637889+0j), (0.005178233153769519+0j), (0.005050266182175896+0j), (0.004924330990907584+0j), (0.004800434008786394+0j), (0.0046785801177264925+0j), (0.00455877268722638+0j), (0.0044410136097028765+0j), (0.004325303336597747+0j), (0.004211640915188053+0j), (0.004100024026032072+0j), (0.003990449020983293+0j), (0.003882910961705928+0j), (0.003777403658626311+0j), (0.003673919710255625+0j), (0.003572450542820513+0j), (0.0034729864501394066+0j), (0.0033755166336836644+0j), (0.0032800292427640244+0j), (0.003186511414784307+0j), (0.0030949493155058507+0j), (0.003005328179267689+0j), (0.0029176323491091616+0j), (0.002831845316743303+0j), (0.002747949762331074+0j), (0.002665927594008288+0j), (0.00258575998711888+0j), (0.0025074274231099737+0j), (0.0024309097280461093+0j), (0.0023561861107018293+0j), (0.0022832352001937394+0j), (0.0022120350831150775+0j), (0.0021425633401377245+0j), (0.002074797082048531+0j), (0.002008712985188748+0j), (0.0019442873262672763+0j), (0.001881496016520356+0j), (0.0018203146351922297+0j), (0.0017607184623131857+0j), (0.0017026825107532635+0j), (0.0016461815575317732+0j), (0.001591190174364554+0j), (0.001537682757432755+0j), (0.0014856335563586374+0j), (0.001435016702375662+0j), (0.0013858062356818235+0j), (0.0013379761319668292+0j), (0.0012915003281053841+0j), (0.0012463527470103915+0j), (0.0012025073216414327+0j), (0.0011599380181653847+0j), (0.0011186188582674702+0j), (0.0010785239406124573+0j), (0.0010396274614570445+0j), (0.0010019037344158065+0j), (0.0009653272093842949+0j), (0.0009298724906241083+0j), (0.0008955143540158835+0j), (0.000862227763487262+0j), (0.0008299878866239239+0j), (0.0007987701094727728+0j), (0.0007685500505472943+0j), (0.0007393035740459889+0j), (0.0007110068022956224+0j), (0.0006836361274318032+0j), (0.0006571682223301327+0j), (0.0006315800508018443+0j), (0.0006068488770684752+0j), (0.0005829522745306895+0j), (0.00055986813384689+0j), (0.0005375746703377424+0j), (0.0005160504307331536+0j), (0.0004952742992786395+0j), (0.0004752255032183401+0j), (0.000455883617672247+0j), (0.0004372285699254432+0j), (0.00041924064314737306+0j), (0.00040190047955931577+0j), (0.00038518908306837523+0j), (0.0003690878213863702+0j), (0.00035357842765207934+0j), (0.00033864300157529585+0j), (0.00032426401012114085+0j), (0.0003104242877530255+0j), (0.00029710703625257837+0j), (0.00028429582413473973+0j), (0.00027197458567608827+0j), (0.00026012761957429825+0j), (0.00024873958725643775+0j), (0.00023779551085360574+0j), (0.000227280770859166+0j), (0.00021718110348758075+0j), (0.0002074825977505767+0j)],
        },
        "q4_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007285172954878752, 0.0019803153260428198, 0.0048169694065816285, 0.010484759790527026, 0.02042152355629078, 0.035592857172064334, 0.055511456392513564, 0.07747247827601657, 0.0967514168737607, 0.10812155328422088] + [0.10963371836252556] * 32 + [0.10812155328422088, 0.0967514168737607, 0.07747247827601657, 0.055511456392513564, 0.035592857172064334, 0.02042152355629078, 0.010484759790527026, 0.0048169694065816285, 0.0019803153260428198, 0.0007285172954878752],
        },
        "q4_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002884749000429387, -0.0007016133336213376, -0.0015058430574422168, -0.002840641328456392, -0.004681611688651863, -0.006676055296575471, -0.008098325442558795, -0.008072945435732759, -0.006049133266156289, -0.002253340591430135] + [0.0] * 32 + [0.002253340591430135, 0.006049133266156289, 0.008072945435732759, 0.008098325442558795, 0.006676055296575471, 0.004681611688651863, 0.002840641328456392, 0.0015058430574422168, 0.0007016133336213376, 0.0002884749000429387],
        },
        "q4_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003639874941886334, 0.0009894205912393044, 0.002406691831126384, 0.005238477476046673, 0.010203160903394286, 0.01778318095303098, 0.027735066876540457, 0.03870740394349351, 0.04833969763682312, 0.054020533886365844] + [0.05477605359888424] * 32 + [0.054020533886365844, 0.04833969763682312, 0.03870740394349351, 0.027735066876540457, 0.01778318095303098, 0.010203160903394286, 0.005238477476046673, 0.002406691831126384, 0.0009894205912393044, 0.0003639874941886334],
        },
        "q4_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00014413007989416126, -0.00035054552688847535, -0.0007523610551382784, -0.001419263379795382, -0.0023390633521959653, -0.0033355428258404368, -0.0040461485310201405, -0.004033467974025384, -0.0030223151505096636, -0.0011258316041473284] + [0.0] * 32 + [0.0011258316041473284, 0.0030223151505096636, 0.004033467974025384, 0.0040461485310201405, 0.0033355428258404368, 0.0023390633521959653, 0.001419263379795382, 0.0007523610551382784, 0.00035054552688847535, 0.00014413007989416126],
        },
        "q4_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003639874941886334, -0.0009894205912393044, -0.002406691831126384, -0.005238477476046673, -0.010203160903394286, -0.01778318095303098, -0.027735066876540457, -0.03870740394349351, -0.04833969763682312, -0.054020533886365844] + [-0.05477605359888424] * 32 + [-0.054020533886365844, -0.04833969763682312, -0.03870740394349351, -0.027735066876540457, -0.01778318095303098, -0.010203160903394286, -0.005238477476046673, -0.002406691831126384, -0.0009894205912393044, -0.0003639874941886334],
        },
        "q4_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00014413007989416126, 0.00035054552688847535, 0.0007523610551382784, 0.001419263379795382, 0.0023390633521959653, 0.0033355428258404368, 0.0040461485310201405, 0.004033467974025384, 0.0030223151505096636, 0.0011258316041473284] + [0.0] * 32 + [-0.0011258316041473284, -0.0030223151505096636, -0.004033467974025384, -0.0040461485310201405, -0.0033355428258404368, -0.0023390633521959653, -0.001419263379795382, -0.0007523610551382784, -0.00035054552688847535, -0.00014413007989416126],
        },
        "q4_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002892050169086339, 0.0007033890850922535, 0.001509654277805461, 0.0028478308625995295, 0.004693460635135636, 0.006692952089217112, 0.008118821936321756, 0.008093377693851534, 0.006064443347621959, 0.0022590436940907606] + [0.0] * 32 + [-0.0022590436940907606, -0.006064443347621959, -0.008093377693851534, -0.008118821936321756, -0.006692952089217112, -0.004693460635135636, -0.0028478308625995295, -0.001509654277805461, -0.0007033890850922535, -0.0002892050169086339],
        },
        "q4_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0007303611396639445, 0.0019853274141611392, 0.0048291609372997585, 0.010511296241201545, 0.02047320950459831, 0.035682941076472435, 0.0556519533665846, 0.0776685575987171, 0.09699629031414987, 0.1083952040232842] + [0.1099111963226997] * 32 + [0.1083952040232842, 0.09699629031414987, 0.0776685575987171, 0.0556519533665846, 0.035682941076472435, 0.02047320950459831, 0.010511296241201545, 0.0048291609372997585, 0.0019853274141611392, 0.0007303611396639445],
        },
        "q4_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0001441730279450845, 0.0003506499828573527, 0.0007525852445714104, 0.0014196862935685077, 0.0023397603490479518, 0.0033365367548193565, 0.004047354207123843, 0.004034669871561781, 0.0030232157435370562, 0.001126167080774424] + [0.0] * 32 + [-0.001126167080774424, -0.0030232157435370562, -0.004034669871561781, -0.004047354207123843, -0.0033365367548193565, -0.0023397603490479518, -0.0014196862935685077, -0.0007525852445714104, -0.0003506499828573527, -0.0001441730279450845],
        },
        "q4_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00036409595561075507, 0.0009897154199521466, 0.002407408979992156, 0.005240038443733408, 0.010206201253294727, 0.017788480006231455, 0.027743331404426988, 0.038718938021299415, 0.04835410195684601, 0.05403663098866368] + [0.05479237583183565] * 32 + [0.05403663098866368, 0.04835410195684601, 0.038718938021299415, 0.027743331404426988, 0.017788480006231455, 0.010206201253294727, 0.005240038443733408, 0.002407408979992156, 0.0009897154199521466, 0.00036409595561075507],
        },
        "q4_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002454983391833253, 0.0005970880243906021, 0.0012815048020392023, 0.0024174468151224146, 0.0039841521535988085, 0.005681466523990009, 0.006891848982418661, 0.006870250051200291, 0.005147942403720139, 0.0019176412669806935] + [0.0] * 32 + [-0.0019176412669806935, -0.005147942403720139, -0.006870250051200291, -0.006891848982418661, -0.005681466523990009, -0.0039841521535988085, -0.0024174468151224146, -0.0012815048020392023, -0.0005970880243906021, -0.0002454983391833253],
        },
        "q4_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q4_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q4_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002454983391833253, -0.0005970880243906021, -0.0012815048020392023, -0.0024174468151224146, -0.0039841521535988085, -0.005681466523990009, -0.006891848982418661, -0.006870250051200291, -0.005147942403720139, -0.0019176412669806935] + [0.0] * 32 + [0.0019176412669806935, 0.005147942403720139, 0.006870250051200291, 0.006891848982418661, 0.005681466523990009, 0.0039841521535988085, 0.0024174468151224146, 0.0012815048020392023, 0.0005970880243906021, 0.0002454983391833253],
        },
        "q4_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0001441730279450845, -0.0003506499828573527, -0.0007525852445714104, -0.0014196862935685077, -0.0023397603490479518, -0.0033365367548193565, -0.004047354207123843, -0.004034669871561781, -0.0030232157435370562, -0.001126167080774424] + [0.0] * 32 + [0.001126167080774424, 0.0030232157435370562, 0.004034669871561781, 0.004047354207123843, 0.0033365367548193565, 0.0023397603490479518, 0.0014196862935685077, 0.0007525852445714104, 0.0003506499828573527, 0.0001441730279450845],
        },
        "q4_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00036409595561075507, -0.0009897154199521466, -0.002407408979992156, -0.005240038443733408, -0.010206201253294727, -0.017788480006231455, -0.027743331404426988, -0.038718938021299415, -0.04835410195684601, -0.05403663098866368] + [-0.05479237583183565] * 32 + [-0.05403663098866368, -0.04835410195684601, -0.038718938021299415, -0.027743331404426988, -0.017788480006231455, -0.010206201253294727, -0.005240038443733408, -0.002407408979992156, -0.0009897154199521466, -0.00036409595561075507],
        },
        "q5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0008720809757939942+0j), (0.0023705618694456468+0j), (0.005766215032202263+0j), (0.012550916231803613+0j), (0.024445846791109577+0j), (0.04260688635143973+0j), (0.06645070111356702+0j), (0.09273942412977619+0j), (0.11581752493633832+0j), (0.12942829261084438+0j)] + [(0.13123844921964034+0j)] * 32 + [(0.12942829261084438+0j), (0.11581752493633832+0j), (0.09273942412977619+0j), (0.06645070111356702+0j), (0.04260688635143973+0j), (0.024445846791109577+0j), (0.012550916231803613+0j), (0.005766215032202263+0j), (0.0023705618694456468+0j), (0.0008720809757939942+0j)],
        },
        "q5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00023390439715249725+0j), (0.0006358180723763009+0j), (0.0015465800635439412+0j), (0.0033663324581053593+0j), (0.006556720322159072+0j), (0.011427766851013911+0j), (0.017823013706013142+0j), (0.02487401938059161+0j), (0.03106389097097776+0j), (0.034714490509385854+0j)] + [(0.0352+0j)] * 32 + [(0.034714490509385854+0j), (0.03106389097097776+0j), (0.02487401938059161+0j), (0.017823013706013142+0j), (0.011427766851013911+0j), (0.006556720322159072+0j), (0.0033663324581053593+0j), (0.0015465800635439412+0j), (0.0006358180723763009+0j), (0.00023390439715249725+0j)],
        },
        "q5_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00023390439715249725+0j), (0.0006358180723763009+0j), (0.0015465800635439412+0j), (0.0033663324581053593+0j), (0.006556720322159072+0j), (0.011427766851013911+0j), (0.017823013706013142+0j), (0.02487401938059161+0j), (0.03106389097097776+0j), (0.034714490509385854+0j)] + [(0.0352+0j)] * 32 + [(0.034714490509385854+0j), (0.03106389097097776+0j), (0.02487401938059161+0j), (0.017823013706013142+0j), (0.011427766851013911+0j), (0.006556720322159072+0j), (0.0033663324581053593+0j), (0.0015465800635439412+0j), (0.0006358180723763009+0j), (0.00023390439715249725+0j)],
        },
        "q5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00043027546606994526+0j), (0.0011696099806496787+0j), (0.0028449890885206483+0j), (0.006192488405480169+0j), (0.012061320466190116+0j), (0.02102178397592465+0j), (0.032786068250465775+0j), (0.04575664422007058+0j), (0.05714313338354751+0j), (0.06385854120377411+0j)] + [(0.06475165319695818+0j)] * 32 + [(0.06385854120377411+0j), (0.05714313338354751+0j), (0.04575664422007058+0j), (0.032786068250465775+0j), (0.02102178397592465+0j), (0.012061320466190116+0j), (0.006192488405480169+0j), (0.0028449890885206483+0j), (0.0011696099806496787+0j), (0.00043027546606994526+0j)],
        },
        "q5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00043027546606994526+0j), (-0.0011696099806496787+0j), (-0.0028449890885206483+0j), (-0.006192488405480169+0j), (-0.012061320466190116+0j), (-0.02102178397592465+0j), (-0.032786068250465775+0j), (-0.04575664422007058+0j), (-0.05714313338354751+0j), (-0.06385854120377411+0j)] + [(-0.06475165319695818+0j)] * 32 + [(-0.06385854120377411+0j), (-0.05714313338354751+0j), (-0.04575664422007058+0j), (-0.032786068250465775+0j), (-0.02102178397592465+0j), (-0.012061320466190116+0j), (-0.006192488405480169+0j), (-0.0028449890885206483+0j), (-0.0011696099806496787+0j), (-0.00043027546606994526+0j)],
        },
        "q5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0008677730473957577+0j), (0.002358851705962418+0j), (0.005737730932471792+0j), (0.01248891688775228+0j), (0.02432508855817774+0j), (0.042396415740603745+0j), (0.06612244620335157+0j), (0.09228130749848398+0j), (0.11524540649947819+0j), (0.1287889393480744+0j)] + [(0.13059015409794128+0j)] * 32 + [(0.1287889393480744+0j), (0.11524540649947819+0j), (0.09228130749848398+0j), (0.06612244620335157+0j), (0.042396415740603745+0j), (0.02432508855817774+0j), (0.01248891688775228+0j), (0.005737730932471792+0j), (0.002358851705962418+0j), (0.0008677730473957577+0j)],
        },
        "q5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00043027546606994526+0j), (0.0011696099806496787+0j), (0.0028449890885206483+0j), (0.006192488405480169+0j), (0.012061320466190116+0j), (0.02102178397592465+0j), (0.032786068250465775+0j), (0.04575664422007058+0j), (0.05714313338354751+0j), (0.06385854120377411+0j)] + [(0.06475165319695818+0j)] * 32 + [(0.06385854120377411+0j), (0.05714313338354751+0j), (0.04575664422007058+0j), (0.032786068250465775+0j), (0.02102178397592465+0j), (0.012061320466190116+0j), (0.006192488405480169+0j), (0.0028449890885206483+0j), (0.0011696099806496787+0j), (0.00043027546606994526+0j)],
        },
        "q5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00043027546606994526+0j), (-0.0011696099806496787+0j), (-0.0028449890885206483+0j), (-0.006192488405480169+0j), (-0.012061320466190116+0j), (-0.02102178397592465+0j), (-0.032786068250465775+0j), (-0.04575664422007058+0j), (-0.05714313338354751+0j), (-0.06385854120377411+0j)] + [(-0.06475165319695818+0j)] * 32 + [(-0.06385854120377411+0j), (-0.05714313338354751+0j), (-0.04575664422007058+0j), (-0.032786068250465775+0j), (-0.02102178397592465+0j), (-0.012061320466190116+0j), (-0.006192488405480169+0j), (-0.0028449890885206483+0j), (-0.0011696099806496787+0j), (-0.00043027546606994526+0j)],
        },
        "q5_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.000311223896625865+0j), (0.00032577165523137104+0j), (0.0003409211562887489+0j), (0.0003566932662804085+0j), (0.00037310938088465655+0j), (0.0003901914293614473+0j), (0.0004079618785141323+0j), (0.0004264437362021095+0j), (0.0004456605543788675+0j), (0.0004656364316295382+0j), (0.0004863960151817112+0j), (0.0005079645023629436+0j), (0.0005303676414781189+0j), (0.0005536317320795551+0j), (0.0005777836246025627+0j), (0.0006028507193389735+0j), (0.0006288609647210594+0j), (0.0006558428548881647+0j), (0.0006838254265083703+0j), (0.0007128382548275099+0j), (0.000742911448917959+0j), (0.0007740756460997302+0j), (0.0008063620055066135+0j), (0.0008398022007703349+0j), (0.0008744284117960341+0j), (0.0009102733156027127+0j), (0.0009473700762027662+0j), (0.0009857523334951988+0j), (0.0010254541911477047+0j), (0.0010665102034434334+0j), (0.001108955361068983+0j), (0.0011528250758209412+0j), (0.001198155164209159+0j), (0.0012449818299358857+0j), (0.0012933416452308927+0j), (0.001343271531023825+0j), (0.001394808735936162+0j), (0.001447990814076442+0j), (0.0015028556016237094+0j), (0.0015594411921855662+0j), (0.0016177859109186856+0j), (0.001677928287401205+0j), (0.0017399070272480768+0j), (0.0018037609824621485+0j), (0.0018695291205155869+0j), (0.0019372504921580757+0j), (0.0020069641979502434+0j), (0.0020787093535227347+0j), (0.002152525053563493+0j), (0.0022284503345379554+0j), (0.0023065241361491322+0j), (0.0023867852615468304+0j), (0.002469272336297659+0j), (0.0025540237661298947+0j), (0.0026410776934697776+0j), (0.0027304719527883443+0j), (0.0028222440247805333+0j), (0.0029164309894009134+0j), (0.0030130694777831214+0j), (0.0031121956230727955+0j), (0.003213845010206586+0j), (0.003318052624672616+0j), (0.0034248528002906085+0j), (0.003534279166052743+0j), (0.0036463645920691633+0j), (0.0037611411346649593+0j), (0.0038786399806783195+0j), (0.003998891391012432+0j), (0.00412192464349661+0j), (0.004247767975114953+0j), (0.0043764485236637415+0j), (0.004507992268901533+0j), (0.0046424239732587745+0j), (0.00477976712217646+0j), (0.004920043864146036+0j), (0.0050632749505254955+0j), (0.005209479675209109+0j), (0.005358675814230768+0j), (0.005510879565383436+0j), (0.005666105487939465+0j), (0.005824366442558891+0j), (0.005985673531474939+0j), (0.006150036039048107+0j), (0.0063174613727820786+0j), (0.006487955004896619+0j), (0.006661520414554313+0j), (0.006838159030839568+0j), (0.0070178701765897375+0j), (0.007200651013179588+0j), (0.007386496486361374+0j), (0.007575399273263843+0j), (0.0077673497306542764+0j), (0.007962335844568335+0j), (0.008160343181412896+0j), (0.008361354840647449+0j), (0.008565351409149572+0j), (0.00877231091737005+0j), (0.008982208797382775+0j), (0.009195017842934177+0j), (0.009410708171596123+0j), (0.009629247189125369+0j), (0.009850599556131497+0j), (0.010074727157153912+0j), (0.010301589072246911+0j), (0.010531141551170058+0j), (0.010763337990279074+0j), (0.010998128912210215+0j), (0.011235461948448692+0j), (0.011475281824868948+0j), (0.011717530350331776+0j), (0.011962146408420072+0j), (0.01220906595239174+0j), (0.01245822200342467+0j), (0.012709544652224925+0j), (0.01296296106406537+0j), (0.013218395487317664+0j), (0.013475769265536262+0j), (0.013735000853148428+0j), (0.013996005834799456+0j), (0.014258696948397421+0j), (0.01452298411189651+0j), (0.014788774453852823+0j), (0.015055972347780855+0j), (0.015324479450333491+0j), (0.01559419474332229+0j), (0.015865014579589134+0j), (0.01613683273273416+0j), (0.016409540450698784+0j), (0.01668302651319626+0j), (0.016957177292976036+0j), (0.017231876820901517+0j), (0.017507006854814478+0j), (0.017782446952152715+0j), (0.018058074546280917+0j), (0.018333765026488123+0j), (0.01860939182159837+0j), (0.018884826487134514+0j), (0.019159938795968574+0j), (0.01943459683238516+0j), (0.019708667089478053+0j), (0.019982014569793396+0j), (0.02025450288912642+0j), (0.020525994383372263+0j), (0.02079635021832506+0j), (0.021065430502313257+0j), (0.021333094401553034+0j), (0.021599200258095815+0j), (0.02186360571023976+0j), (0.022126167815269906+0j), (0.02238674317438578+0j), (0.02264518805967022+0j), (0.022901358542948013+0j), (0.02315511062637814+0j), (0.023406300374618723+0j), (0.0236547840483995+0j), (0.02390041823933236+0j), (0.02414306000578686+0j), (0.02438256700965382+0j), (0.02461879765381692+0j), (0.024851611220149287+0j), (0.02508086800784923+0j), (0.025306429471927034+0j), (0.025528158361652602+0j), (0.025745918858772126+0j), (0.025959576715300386+0j), (0.026168999390694562+0j), (0.026374056188214413+0j), (0.026574618390273603+0j), (0.026770559392586914+0j), (0.026961754836918376+0j), (0.027148082742236273+0j), (0.02732942363408195+0j), (0.027505660671960867+0j), (0.027676679774566282+0j), (0.027842369742647952+0j), (0.028002622379341046+0j), (0.028157332607773172+0j), (0.02830639858577082+0j), (0.02844972181749017+0j), (0.02858720726180099+0j), (0.028718763437256954+0j), (0.028844302523490076+0j), (0.028963740458872005+0j), (0.029076997034290324+0j), (0.029183995982893302+0j), (0.029284665065662692+0j), (0.02937893615268013+0j), (0.02946674529995916+0j), (0.029548032821721682+0j), (0.029622743358004387+0j), (0.029690825937488025+0j), (0.0297522340354497+0j), (0.029806925626745914+0j), (0.029854863233741962+0j), (0.02989601396911107+0j), (0.02993034957343494+0j), (0.029957846447545455+0j), (0.0299784856795558+0j), (0.029992253066537564+0j), (0.029999139130809132+0j)] + [(0.03+0j)] * 2400 + [(0.029999139130809132+0j), (0.029992253066537564+0j), (0.0299784856795558+0j), (0.029957846447545455+0j), (0.02993034957343494+0j), (0.02989601396911107+0j), (0.029854863233741962+0j), (0.029806925626745914+0j), (0.0297522340354497+0j), (0.029690825937488025+0j), (0.029622743358004387+0j), (0.029548032821721682+0j), (0.02946674529995916+0j), (0.02937893615268013+0j), (0.029284665065662692+0j), (0.029183995982893302+0j), (0.029076997034290324+0j), (0.028963740458872005+0j), (0.028844302523490076+0j), (0.028718763437256954+0j), (0.02858720726180099+0j), (0.02844972181749017+0j), (0.02830639858577082+0j), (0.028157332607773172+0j), (0.028002622379341046+0j), (0.027842369742647952+0j), (0.027676679774566282+0j), (0.027505660671960867+0j), (0.02732942363408195+0j), (0.027148082742236273+0j), (0.026961754836918376+0j), (0.026770559392586914+0j), (0.026574618390273603+0j), (0.026374056188214413+0j), (0.026168999390694562+0j), (0.025959576715300386+0j), (0.025745918858772126+0j), (0.025528158361652602+0j), (0.025306429471927034+0j), (0.02508086800784923+0j), (0.024851611220149287+0j), (0.02461879765381692+0j), (0.02438256700965382+0j), (0.02414306000578686+0j), (0.02390041823933236+0j), (0.0236547840483995+0j), (0.023406300374618723+0j), (0.02315511062637814+0j), (0.022901358542948013+0j), (0.02264518805967022+0j), (0.02238674317438578+0j), (0.022126167815269906+0j), (0.02186360571023976+0j), (0.021599200258095815+0j), (0.021333094401553034+0j), (0.021065430502313257+0j), (0.02079635021832506+0j), (0.020525994383372263+0j), (0.02025450288912642+0j), (0.019982014569793396+0j), (0.019708667089478053+0j), (0.01943459683238516+0j), (0.019159938795968574+0j), (0.018884826487134514+0j), (0.01860939182159837+0j), (0.018333765026488123+0j), (0.018058074546280917+0j), (0.017782446952152715+0j), (0.017507006854814478+0j), (0.017231876820901517+0j), (0.016957177292976036+0j), (0.01668302651319626+0j), (0.016409540450698784+0j), (0.01613683273273416+0j), (0.015865014579589134+0j), (0.01559419474332229+0j), (0.015324479450333491+0j), (0.015055972347780855+0j), (0.014788774453852823+0j), (0.01452298411189651+0j), (0.014258696948397421+0j), (0.013996005834799456+0j), (0.013735000853148428+0j), (0.013475769265536262+0j), (0.013218395487317664+0j), (0.01296296106406537+0j), (0.012709544652224925+0j), (0.01245822200342467+0j), (0.01220906595239174+0j), (0.011962146408420072+0j), (0.011717530350331776+0j), (0.011475281824868948+0j), (0.011235461948448692+0j), (0.010998128912210215+0j), (0.010763337990279074+0j), (0.010531141551170058+0j), (0.010301589072246911+0j), (0.010074727157153912+0j), (0.009850599556131497+0j), (0.009629247189125369+0j), (0.009410708171596123+0j), (0.009195017842934177+0j), (0.008982208797382775+0j), (0.00877231091737005+0j), (0.008565351409149572+0j), (0.008361354840647449+0j), (0.008160343181412896+0j), (0.007962335844568335+0j), (0.0077673497306542764+0j), (0.007575399273263843+0j), (0.007386496486361374+0j), (0.007200651013179588+0j), (0.0070178701765897375+0j), (0.006838159030839568+0j), (0.006661520414554313+0j), (0.006487955004896619+0j), (0.0063174613727820786+0j), (0.006150036039048107+0j), (0.005985673531474939+0j), (0.005824366442558891+0j), (0.005666105487939465+0j), (0.005510879565383436+0j), (0.005358675814230768+0j), (0.005209479675209109+0j), (0.0050632749505254955+0j), (0.004920043864146036+0j), (0.00477976712217646+0j), (0.0046424239732587745+0j), (0.004507992268901533+0j), (0.0043764485236637415+0j), (0.004247767975114953+0j), (0.00412192464349661+0j), (0.003998891391012432+0j), (0.0038786399806783195+0j), (0.0037611411346649593+0j), (0.0036463645920691633+0j), (0.003534279166052743+0j), (0.0034248528002906085+0j), (0.003318052624672616+0j), (0.003213845010206586+0j), (0.0031121956230727955+0j), (0.0030130694777831214+0j), (0.0029164309894009134+0j), (0.0028222440247805333+0j), (0.0027304719527883443+0j), (0.0026410776934697776+0j), (0.0025540237661298947+0j), (0.002469272336297659+0j), (0.0023867852615468304+0j), (0.0023065241361491322+0j), (0.0022284503345379554+0j), (0.002152525053563493+0j), (0.0020787093535227347+0j), (0.0020069641979502434+0j), (0.0019372504921580757+0j), (0.0018695291205155869+0j), (0.0018037609824621485+0j), (0.0017399070272480768+0j), (0.001677928287401205+0j), (0.0016177859109186856+0j), (0.0015594411921855662+0j), (0.0015028556016237094+0j), (0.001447990814076442+0j), (0.001394808735936162+0j), (0.001343271531023825+0j), (0.0012933416452308927+0j), (0.0012449818299358857+0j), (0.001198155164209159+0j), (0.0011528250758209412+0j), (0.001108955361068983+0j), (0.0010665102034434334+0j), (0.0010254541911477047+0j), (0.0009857523334951988+0j), (0.0009473700762027662+0j), (0.0009102733156027127+0j), (0.0008744284117960341+0j), (0.0008398022007703349+0j), (0.0008063620055066135+0j), (0.0007740756460997302+0j), (0.000742911448917959+0j), (0.0007128382548275099+0j), (0.0006838254265083703+0j), (0.0006558428548881647+0j), (0.0006288609647210594+0j), (0.0006028507193389735+0j), (0.0005777836246025627+0j), (0.0005536317320795551+0j), (0.0005303676414781189+0j), (0.0005079645023629436+0j), (0.0004863960151817112+0j), (0.0004656364316295382+0j), (0.0004456605543788675+0j), (0.0004264437362021095+0j), (0.0004079618785141323+0j), (0.0003901914293614473+0j), (0.00037310938088465655+0j), (0.0003566932662804085+0j), (0.0003409211562887489+0j), (0.00032577165523137104+0j), (0.000311223896625865+0j)],
        },
        "q5_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008720809757939942, 0.0023705618694456468, 0.005766215032202263, 0.012550916231803613, 0.024445846791109577, 0.04260688635143973, 0.06645070111356702, 0.09273942412977619, 0.11581752493633832, 0.12942829261084438] + [0.13123844921964034] * 32 + [0.12942829261084438, 0.11581752493633832, 0.09273942412977619, 0.06645070111356702, 0.04260688635143973, 0.024445846791109577, 0.012550916231803613, 0.005766215032202263, 0.0023705618694456468, 0.0008720809757939942],
        },
        "q5_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005816880558200126, -0.00141475080123382, -0.0030364198768185603, -0.005727940737255914, -0.00944011975000529, -0.01346176608583226, -0.01632966743858337, -0.016278490553436206, -0.012197624710028023, -0.004543692735604421] + [0.0] * 32 + [0.004543692735604421, 0.012197624710028023, 0.016278490553436206, 0.01632966743858337, 0.01346176608583226, 0.00944011975000529, 0.005727940737255914, 0.0030364198768185603, 0.00141475080123382, 0.0005816880558200126],
        },
        "q5_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00043027546606994526, 0.0011696099806496787, 0.0028449890885206483, 0.006192488405480169, 0.012061320466190116, 0.02102178397592465, 0.032786068250465775, 0.04575664422007058, 0.05714313338354751, 0.06385854120377411] + [0.06475165319695818] * 32 + [0.06385854120377411, 0.05714313338354751, 0.04575664422007058, 0.032786068250465775, 0.02102178397592465, 0.012061320466190116, 0.006192488405480169, 0.0028449890885206483, 0.0011696099806496787, 0.00043027546606994526],
        },
        "q5_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002869986919476152, -0.0006980229786798, -0.0014981372303101092, -0.002826104959003266, -0.004657654550360385, -0.00664189202319479, -0.008056884008399047, -0.008031633878285094, -0.00601817813107916, -0.0022418096068554105] + [0.0] * 32 + [0.0022418096068554105, 0.00601817813107916, 0.008031633878285094, 0.008056884008399047, 0.00664189202319479, 0.004657654550360385, 0.002826104959003266, 0.0014981372303101092, 0.0006980229786798, 0.0002869986919476152],
        },
        "q5_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00043027546606994526, -0.0011696099806496787, -0.0028449890885206483, -0.006192488405480169, -0.012061320466190116, -0.02102178397592465, -0.032786068250465775, -0.04575664422007058, -0.05714313338354751, -0.06385854120377411] + [-0.06475165319695818] * 32 + [-0.06385854120377411, -0.05714313338354751, -0.04575664422007058, -0.032786068250465775, -0.02102178397592465, -0.012061320466190116, -0.006192488405480169, -0.0028449890885206483, -0.0011696099806496787, -0.00043027546606994526],
        },
        "q5_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002869986919476152, 0.0006980229786798, 0.0014981372303101092, 0.002826104959003266, 0.004657654550360385, 0.00664189202319479, 0.008056884008399047, 0.008031633878285094, 0.00601817813107916, 0.0022418096068554105] + [0.0] * 32 + [-0.0022418096068554105, -0.00601817813107916, -0.008031633878285094, -0.008056884008399047, -0.00664189202319479, -0.004657654550360385, -0.002826104959003266, -0.0014981372303101092, -0.0006980229786798, -0.0002869986919476152],
        },
        "q5_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.000578814617958006, 0.0014077621782478478, 0.0030214204905466527, 0.0056996457058880136, 0.009393487199723162, 0.013395267301864666, 0.016249001720553706, 0.016198077640321433, 0.012137370564670113, 0.004521247683468351] + [0.0] * 32 + [-0.004521247683468351, -0.012137370564670113, -0.016198077640321433, -0.016249001720553706, -0.013395267301864666, -0.009393487199723162, -0.0056996457058880136, -0.0030214204905466527, -0.0014077621782478478, -0.000578814617958006],
        },
        "q5_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008677730473957577, 0.002358851705962418, 0.005737730932471792, 0.01248891688775228, 0.02432508855817774, 0.042396415740603745, 0.06612244620335157, 0.09228130749848398, 0.11524540649947819, 0.1287889393480744] + [0.13059015409794128] * 32 + [0.1287889393480744, 0.11524540649947819, 0.09228130749848398, 0.06612244620335157, 0.042396415740603745, 0.02432508855817774, 0.01248891688775228, 0.005737730932471792, 0.002358851705962418, 0.0008677730473957577],
        },
        "q5_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002869986919476152, 0.0006980229786798, 0.0014981372303101092, 0.002826104959003266, 0.004657654550360385, 0.00664189202319479, 0.008056884008399047, 0.008031633878285094, 0.00601817813107916, 0.0022418096068554105] + [0.0] * 32 + [-0.0022418096068554105, -0.00601817813107916, -0.008031633878285094, -0.008056884008399047, -0.00664189202319479, -0.004657654550360385, -0.002826104959003266, -0.0014981372303101092, -0.0006980229786798, -0.0002869986919476152],
        },
        "q5_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00043027546606994526, 0.0011696099806496787, 0.0028449890885206483, 0.006192488405480169, 0.012061320466190116, 0.02102178397592465, 0.032786068250465775, 0.04575664422007058, 0.05714313338354751, 0.06385854120377411] + [0.06475165319695818] * 32 + [0.06385854120377411, 0.05714313338354751, 0.04575664422007058, 0.032786068250465775, 0.02102178397592465, 0.012061320466190116, 0.006192488405480169, 0.0028449890885206483, 0.0011696099806496787, 0.00043027546606994526],
        },
        "q5_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00015601692710188027, 0.00037945608546537004, 0.0008144105656501313, 0.0015363143587133643, 0.002531973039730627, 0.0036106352142903976, 0.004379846738939619, 0.00436612037774066, 0.003271574697399972, 0.0012186823697192873] + [0.0] * 32 + [-0.0012186823697192873, -0.003271574697399972, -0.00436612037774066, -0.004379846738939619, -0.0036106352142903976, -0.002531973039730627, -0.0015363143587133643, -0.0008144105656501313, -0.00037945608546537004, -0.00015601692710188027],
        },
        "q5_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00023390439715249725, 0.0006358180723763009, 0.0015465800635439412, 0.0033663324581053593, 0.006556720322159072, 0.011427766851013911, 0.017823013706013142, 0.02487401938059161, 0.03106389097097776, 0.034714490509385854] + [0.0352] * 32 + [0.034714490509385854, 0.03106389097097776, 0.02487401938059161, 0.017823013706013142, 0.011427766851013911, 0.006556720322159072, 0.0033663324581053593, 0.0015465800635439412, 0.0006358180723763009, 0.00023390439715249725],
        },
        "q5_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00023390439715249725, 0.0006358180723763009, 0.0015465800635439412, 0.0033663324581053593, 0.006556720322159072, 0.011427766851013911, 0.017823013706013142, 0.02487401938059161, 0.03106389097097776, 0.034714490509385854] + [0.0352] * 32 + [0.034714490509385854, 0.03106389097097776, 0.02487401938059161, 0.017823013706013142, 0.011427766851013911, 0.006556720322159072, 0.0033663324581053593, 0.0015465800635439412, 0.0006358180723763009, 0.00023390439715249725],
        },
        "q5_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00015601692710188027, -0.00037945608546537004, -0.0008144105656501313, -0.0015363143587133643, -0.002531973039730627, -0.0036106352142903976, -0.004379846738939619, -0.00436612037774066, -0.003271574697399972, -0.0012186823697192873] + [0.0] * 32 + [0.0012186823697192873, 0.003271574697399972, 0.00436612037774066, 0.004379846738939619, 0.0036106352142903976, 0.002531973039730627, 0.0015363143587133643, 0.0008144105656501313, 0.00037945608546537004, 0.00015601692710188027],
        },
        "q5_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002869986919476152, -0.0006980229786798, -0.0014981372303101092, -0.002826104959003266, -0.004657654550360385, -0.00664189202319479, -0.008056884008399047, -0.008031633878285094, -0.00601817813107916, -0.0022418096068554105] + [0.0] * 32 + [0.0022418096068554105, 0.00601817813107916, 0.008031633878285094, 0.008056884008399047, 0.00664189202319479, 0.004657654550360385, 0.002826104959003266, 0.0014981372303101092, 0.0006980229786798, 0.0002869986919476152],
        },
        "q5_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00043027546606994526, -0.0011696099806496787, -0.0028449890885206483, -0.006192488405480169, -0.012061320466190116, -0.02102178397592465, -0.032786068250465775, -0.04575664422007058, -0.05714313338354751, -0.06385854120377411] + [-0.06475165319695818] * 32 + [-0.06385854120377411, -0.05714313338354751, -0.04575664422007058, -0.032786068250465775, -0.02102178397592465, -0.012061320466190116, -0.006192488405480169, -0.0028449890885206483, -0.0011696099806496787, -0.00043027546606994526],
        },
        "q6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 76 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0008885405042653874+0j), (0.0024153035065944393+0j), (0.005875045729269468+0j), (0.012787800384529636+0j), (0.024907234119160446+0j), (0.043411042477355034+0j), (0.06770488190328897+0j), (0.09448977442321642+0j), (0.11800344792065792+0j), (0.13187110322862264+0j)] + [(0.13371542446784532+0j)] * 76 + [(0.13187110322862264+0j), (0.11800344792065792+0j), (0.09448977442321642+0j), (0.06770488190328897+0j), (0.043411042477355034+0j), (0.024907234119160446+0j), (0.012787800384529636+0j), (0.005875045729269468+0j), (0.0024153035065944393+0j), (0.0008885405042653874+0j)],
        },
        "q6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.002618373842072091+0j), (0.0071174780350170596+0j), (0.0173127347427056+0j), (0.037683416640836805+0j), (0.0733972733746041+0j), (0.12792476823975737+0j), (0.1995144744726272+0j), (0.27844487955852+0j), (0.3477355729159673+0j), (0.3886011336134702+0j)] + [(0.3940360265260349+0j)] * 76 + [(0.3886011336134702+0j), (0.3477355729159673+0j), (0.27844487955852+0j), (0.1995144744726272+0j), (0.12792476823975737+0j), (0.0733972733746041+0j), (0.037683416640836805+0j), (0.0173127347427056+0j), (0.0071174780350170596+0j), (0.002618373842072091+0j)],
        },
        "q6_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.002618373842072091+0j), (0.0071174780350170596+0j), (0.0173127347427056+0j), (0.037683416640836805+0j), (0.0733972733746041+0j), (0.12792476823975737+0j), (0.1995144744726272+0j), (0.27844487955852+0j), (0.3477355729159673+0j), (0.3886011336134702+0j)] + [(0.3940360265260349+0j)] * 76 + [(0.3886011336134702+0j), (0.3477355729159673+0j), (0.27844487955852+0j), (0.1995144744726272+0j), (0.12792476823975737+0j), (0.0733972733746041+0j), (0.037683416640836805+0j), (0.0173127347427056+0j), (0.0071174780350170596+0j), (0.002618373842072091+0j)],
        },
        "q6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0004395104015456173+0j), (0.0011947131379401897+0j), (0.0029060506472970626+0j), (0.006325396821990164+0j), (0.012320190713369306+0j), (0.021472971259211725+0j), (0.033489750539301665+0j), (0.04673871196568297+0j), (0.058369587576938574+0j), (0.06522912715182705+0j)] + [(0.06614140786895659+0j)] * 76 + [(0.06522912715182705+0j), (0.058369587576938574+0j), (0.04673871196568297+0j), (0.033489750539301665+0j), (0.021472971259211725+0j), (0.012320190713369306+0j), (0.006325396821990164+0j), (0.0029060506472970626+0j), (0.0011947131379401897+0j), (0.0004395104015456173+0j)],
        },
        "q6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0004395104015456173+0j), (-0.0011947131379401897+0j), (-0.0029060506472970626+0j), (-0.006325396821990164+0j), (-0.012320190713369306+0j), (-0.021472971259211725+0j), (-0.033489750539301665+0j), (-0.04673871196568297+0j), (-0.058369587576938574+0j), (-0.06522912715182705+0j)] + [(-0.06614140786895659+0j)] * 76 + [(-0.06522912715182705+0j), (-0.058369587576938574+0j), (-0.04673871196568297+0j), (-0.033489750539301665+0j), (-0.021472971259211725+0j), (-0.012320190713369306+0j), (-0.006325396821990164+0j), (-0.0029060506472970626+0j), (-0.0011947131379401897+0j), (-0.0004395104015456173+0j)],
        },
        "q6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0008903554366180133+0j), (0.002420237004228465+0j), (0.005887046094493137+0j), (0.012813920738667+0j), (0.024958109622078197+0j), (0.04349971384920038+0j), (0.06784317585838401+0j), (0.09468277918526134+0j), (0.11824448169944966+0j), (0.13214046307263333+0j)] + [(0.13398855152142003+0j)] * 76 + [(0.13214046307263333+0j), (0.11824448169944966+0j), (0.09468277918526134+0j), (0.06784317585838401+0j), (0.04349971384920038+0j), (0.024958109622078197+0j), (0.012813920738667+0j), (0.005887046094493137+0j), (0.002420237004228465+0j), (0.0008903554366180133+0j)],
        },
        "q6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0004395066070840293+0j), (0.0011947028235242063+0j), (0.0029060255582490785+0j), (0.006325342212417363+0j), (0.012320084348445394+0j), (0.0214727858748287+0j), (0.03348946140946181+0j), (0.04673830845248601+0j), (0.058369083649938924+0j), (0.06522856400379569+0j)] + [(0.06614083684485647+0j)] * 76 + [(0.06522856400379569+0j), (0.058369083649938924+0j), (0.04673830845248601+0j), (0.03348946140946181+0j), (0.0214727858748287+0j), (0.012320084348445394+0j), (0.006325342212417363+0j), (0.0029060255582490785+0j), (0.0011947028235242063+0j), (0.0004395066070840293+0j)],
        },
        "q6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0004395066070840293+0j), (-0.0011947028235242063+0j), (-0.0029060255582490785+0j), (-0.006325342212417363+0j), (-0.012320084348445394+0j), (-0.0214727858748287+0j), (-0.03348946140946181+0j), (-0.04673830845248601+0j), (-0.058369083649938924+0j), (-0.06522856400379569+0j)] + [(-0.06614083684485647+0j)] * 76 + [(-0.06522856400379569+0j), (-0.058369083649938924+0j), (-0.04673830845248601+0j), (-0.03348946140946181+0j), (-0.0214727858748287+0j), (-0.012320084348445394+0j), (-0.006325342212417363+0j), (-0.0029060255582490785+0j), (-0.0011947028235242063+0j), (-0.0004395066070840293+0j)],
        },
        "q6_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0002074825977505767+0j), (0.00021718110348758075+0j), (0.000227280770859166+0j), (0.00023779551085360574+0j), (0.00024873958725643775+0j), (0.00026012761957429825+0j), (0.00027197458567608827+0j), (0.00028429582413473973+0j), (0.00029710703625257837+0j), (0.0003104242877530255+0j), (0.00032426401012114085+0j), (0.00033864300157529585+0j), (0.00035357842765207934+0j), (0.0003690878213863702+0j), (0.00038518908306837523+0j), (0.00040190047955931577+0j), (0.00041924064314737306+0j), (0.0004372285699254432+0j), (0.000455883617672247+0j), (0.0004752255032183401+0j), (0.0004952742992786395+0j), (0.0005160504307331536+0j), (0.0005375746703377424+0j), (0.00055986813384689+0j), (0.0005829522745306895+0j), (0.0006068488770684752+0j), (0.0006315800508018443+0j), (0.0006571682223301327+0j), (0.0006836361274318032+0j), (0.0007110068022956224+0j), (0.0007393035740459889+0j), (0.0007685500505472943+0j), (0.0007987701094727728+0j), (0.0008299878866239239+0j), (0.000862227763487262+0j), (0.0008955143540158835+0j), (0.0009298724906241083+0j), (0.0009653272093842949+0j), (0.0010019037344158065+0j), (0.0010396274614570445+0j), (0.0010785239406124573+0j), (0.0011186188582674702+0j), (0.0011599380181653847+0j), (0.0012025073216414327+0j), (0.0012463527470103915+0j), (0.0012915003281053841+0j), (0.0013379761319668292+0j), (0.0013858062356818235+0j), (0.001435016702375662+0j), (0.0014856335563586374+0j), (0.001537682757432755+0j), (0.001591190174364554+0j), (0.0016461815575317732+0j), (0.0017026825107532635+0j), (0.0017607184623131857+0j), (0.0018203146351922297+0j), (0.001881496016520356+0j), (0.0019442873262672763+0j), (0.002008712985188748+0j), (0.002074797082048531+0j), (0.0021425633401377245+0j), (0.0022120350831150775+0j), (0.0022832352001937394+0j), (0.0023561861107018293+0j), (0.0024309097280461093+0j), (0.0025074274231099737+0j), (0.00258575998711888+0j), (0.002665927594008288+0j), (0.002747949762331074+0j), (0.002831845316743303+0j), (0.0029176323491091616+0j), (0.003005328179267689+0j), (0.0030949493155058507+0j), (0.003186511414784307+0j), (0.0032800292427640244+0j), (0.0033755166336836644+0j), (0.0034729864501394066+0j), (0.003572450542820513+0j), (0.003673919710255625+0j), (0.003777403658626311+0j), (0.003882910961705928+0j), (0.003990449020983293+0j), (0.004100024026032072+0j), (0.004211640915188053+0j), (0.004325303336597747+0j), (0.0044410136097028765+0j), (0.00455877268722638+0j), (0.0046785801177264925+0j), (0.004800434008786394+0j), (0.004924330990907584+0j), (0.005050266182175896+0j), (0.005178233153769519+0j), (0.00530822389637889+0j), (0.005440228787608598+0j), (0.005574236560431633+0j), (0.005710234272766382+0j), (0.005848207278246701+0j), (0.005988139198255185+0j), (0.006130011895289452+0j), (0.00627380544773075+0j), (0.00641949812608358+0j), (0.0065670663707543325+0j), (0.006716484771435942+0j), (0.006867726048164609+0j), (0.007020761034113373+0j), (0.00717555866018605+0j), (0.007332085941473478+0j), (0.007490307965632463+0j), (0.007650187883245967+0j), (0.007811686900221186+0j), (0.00797476427228005+0j), (0.008139377301594496+0j), (0.008305481335616448+0j), (0.008473029768149952+0j), (0.008641974042710249+0j), (0.008812263658211777+0j), (0.008983846177024177+0j), (0.009156667235432287+0j), (0.009330670556532972+0j), (0.009505797965598282+0j), (0.009681989407931009+0j), (0.009859182969235217+0j), (0.010037314898520572+0j), (0.010216319633555664+0j), (0.010396129828881528+0j), (0.010576676386392758+0j), (0.010757888488489442+0j), (0.010939693633799192+0j), (0.011122017675464176+0j), (0.011304784861984028+0j), (0.011487917880601016+0j), (0.011671337903209655+0j), (0.011854964634768478+0j), (0.01203871636418728+0j), (0.012222510017658752+0j), (0.012406261214398915+0j), (0.012589884324756344+0j), (0.012773292530645719+0j), (0.012956397888256777+0j), (0.013139111392985372+0j), (0.013321343046528933+0j), (0.013503001926084283+0j), (0.013683996255581513+0j), (0.013864233478883378+0j), (0.014043620334875507+0j), (0.014222062934368694+0j), (0.014399466838730546+0j), (0.014575737140159844+0j), (0.014750778543513275+0j), (0.014924495449590524+0j), (0.01509679203978015+0j), (0.015267572361965345+0j), (0.015436740417585429+0j), (0.01560420024974582+0j), (0.015769856032266338+0j), (0.01593361215955491+0j), (0.016095373337191243+0j), (0.016255044673102553+0j), (0.016412531769211283+0j), (0.01656774081343286+0j), (0.01672057867189949+0j), (0.016870952981284694+0j), (0.01701877224110174+0j), (0.017163945905848087+0j), (0.01730638447686693+0j), (0.017445999593796377+0j), (0.01758270412547628+0j), (0.017716412260182408+0j), (0.017847039595057946+0j), (0.017974503224612255+0j), (0.01809872182815752+0j), (0.018219615756054637+0j), (0.018337107114640584+0j), (0.01845111984971086+0j), (0.018561579828431974+0j), (0.018668414919560703+0j), (0.018771555071848786+0j), (0.018870932390513885+0j), (0.018966481211660117+0j), (0.019058138174533997+0j), (0.019145842291504643+0j), (0.019229535015660056+0j), (0.019309160305914674+0j), (0.019384664689526886+0j), (0.01945599732192887+0j), (0.019523110043775133+0j), (0.01958595743512009+0j), (0.019644496866639445+0j), (0.01969868854781446+0j), (0.01974849557200293+0j), (0.019793883958325355+0j), (0.019834822690299805+0j), (0.019871283751163947+0j), (0.01990324215582798+0j), (0.019930675979407387+0j), (0.019953566382289963+0j), (0.019971897631696975+0j), (0.019985657119703872+0j), (0.019994835377691714+0j), (0.019999426087206094+0j)] + [(0.020000000000000004+0j)] * 2800 + [(0.019999426087206094+0j), (0.019994835377691714+0j), (0.019985657119703872+0j), (0.019971897631696975+0j), (0.019953566382289963+0j), (0.019930675979407387+0j), (0.01990324215582798+0j), (0.019871283751163947+0j), (0.019834822690299805+0j), (0.019793883958325355+0j), (0.01974849557200293+0j), (0.01969868854781446+0j), (0.019644496866639445+0j), (0.01958595743512009+0j), (0.019523110043775133+0j), (0.01945599732192887+0j), (0.019384664689526886+0j), (0.019309160305914674+0j), (0.019229535015660056+0j), (0.019145842291504643+0j), (0.019058138174533997+0j), (0.018966481211660117+0j), (0.018870932390513885+0j), (0.018771555071848786+0j), (0.018668414919560703+0j), (0.018561579828431974+0j), (0.01845111984971086+0j), (0.018337107114640584+0j), (0.018219615756054637+0j), (0.01809872182815752+0j), (0.017974503224612255+0j), (0.017847039595057946+0j), (0.017716412260182408+0j), (0.01758270412547628+0j), (0.017445999593796377+0j), (0.01730638447686693+0j), (0.017163945905848087+0j), (0.01701877224110174+0j), (0.016870952981284694+0j), (0.01672057867189949+0j), (0.01656774081343286+0j), (0.016412531769211283+0j), (0.016255044673102553+0j), (0.016095373337191243+0j), (0.01593361215955491+0j), (0.015769856032266338+0j), (0.01560420024974582+0j), (0.015436740417585429+0j), (0.015267572361965345+0j), (0.01509679203978015+0j), (0.014924495449590524+0j), (0.014750778543513275+0j), (0.014575737140159844+0j), (0.014399466838730546+0j), (0.014222062934368694+0j), (0.014043620334875507+0j), (0.013864233478883378+0j), (0.013683996255581513+0j), (0.013503001926084283+0j), (0.013321343046528933+0j), (0.013139111392985372+0j), (0.012956397888256777+0j), (0.012773292530645719+0j), (0.012589884324756344+0j), (0.012406261214398915+0j), (0.012222510017658752+0j), (0.01203871636418728+0j), (0.011854964634768478+0j), (0.011671337903209655+0j), (0.011487917880601016+0j), (0.011304784861984028+0j), (0.011122017675464176+0j), (0.010939693633799192+0j), (0.010757888488489442+0j), (0.010576676386392758+0j), (0.010396129828881528+0j), (0.010216319633555664+0j), (0.010037314898520572+0j), (0.009859182969235217+0j), (0.009681989407931009+0j), (0.009505797965598282+0j), (0.009330670556532972+0j), (0.009156667235432287+0j), (0.008983846177024177+0j), (0.008812263658211777+0j), (0.008641974042710249+0j), (0.008473029768149952+0j), (0.008305481335616448+0j), (0.008139377301594496+0j), (0.00797476427228005+0j), (0.007811686900221186+0j), (0.007650187883245967+0j), (0.007490307965632463+0j), (0.007332085941473478+0j), (0.00717555866018605+0j), (0.007020761034113373+0j), (0.006867726048164609+0j), (0.006716484771435942+0j), (0.0065670663707543325+0j), (0.00641949812608358+0j), (0.00627380544773075+0j), (0.006130011895289452+0j), (0.005988139198255185+0j), (0.005848207278246701+0j), (0.005710234272766382+0j), (0.005574236560431633+0j), (0.005440228787608598+0j), (0.00530822389637889+0j), (0.005178233153769519+0j), (0.005050266182175896+0j), (0.004924330990907584+0j), (0.004800434008786394+0j), (0.0046785801177264925+0j), (0.00455877268722638+0j), (0.0044410136097028765+0j), (0.004325303336597747+0j), (0.004211640915188053+0j), (0.004100024026032072+0j), (0.003990449020983293+0j), (0.003882910961705928+0j), (0.003777403658626311+0j), (0.003673919710255625+0j), (0.003572450542820513+0j), (0.0034729864501394066+0j), (0.0033755166336836644+0j), (0.0032800292427640244+0j), (0.003186511414784307+0j), (0.0030949493155058507+0j), (0.003005328179267689+0j), (0.0029176323491091616+0j), (0.002831845316743303+0j), (0.002747949762331074+0j), (0.002665927594008288+0j), (0.00258575998711888+0j), (0.0025074274231099737+0j), (0.0024309097280461093+0j), (0.0023561861107018293+0j), (0.0022832352001937394+0j), (0.0022120350831150775+0j), (0.0021425633401377245+0j), (0.002074797082048531+0j), (0.002008712985188748+0j), (0.0019442873262672763+0j), (0.001881496016520356+0j), (0.0018203146351922297+0j), (0.0017607184623131857+0j), (0.0017026825107532635+0j), (0.0016461815575317732+0j), (0.001591190174364554+0j), (0.001537682757432755+0j), (0.0014856335563586374+0j), (0.001435016702375662+0j), (0.0013858062356818235+0j), (0.0013379761319668292+0j), (0.0012915003281053841+0j), (0.0012463527470103915+0j), (0.0012025073216414327+0j), (0.0011599380181653847+0j), (0.0011186188582674702+0j), (0.0010785239406124573+0j), (0.0010396274614570445+0j), (0.0010019037344158065+0j), (0.0009653272093842949+0j), (0.0009298724906241083+0j), (0.0008955143540158835+0j), (0.000862227763487262+0j), (0.0008299878866239239+0j), (0.0007987701094727728+0j), (0.0007685500505472943+0j), (0.0007393035740459889+0j), (0.0007110068022956224+0j), (0.0006836361274318032+0j), (0.0006571682223301327+0j), (0.0006315800508018443+0j), (0.0006068488770684752+0j), (0.0005829522745306895+0j), (0.00055986813384689+0j), (0.0005375746703377424+0j), (0.0005160504307331536+0j), (0.0004952742992786395+0j), (0.0004752255032183401+0j), (0.000455883617672247+0j), (0.0004372285699254432+0j), (0.00041924064314737306+0j), (0.00040190047955931577+0j), (0.00038518908306837523+0j), (0.0003690878213863702+0j), (0.00035357842765207934+0j), (0.00033864300157529585+0j), (0.00032426401012114085+0j), (0.0003104242877530255+0j), (0.00029710703625257837+0j), (0.00028429582413473973+0j), (0.00027197458567608827+0j), (0.00026012761957429825+0j), (0.00024873958725643775+0j), (0.00023779551085360574+0j), (0.000227280770859166+0j), (0.00021718110348758075+0j), (0.0002074825977505767+0j)],
        },
        "q6_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008885405042653874, 0.0024153035065944393, 0.005875045729269468, 0.012787800384529636, 0.024907234119160446, 0.043411042477355034, 0.06770488190328897, 0.09448977442321642, 0.11800344792065792, 0.13187110322862264] + [0.13371542446784532] * 76 + [0.13187110322862264, 0.11800344792065792, 0.09448977442321642, 0.06770488190328897, 0.043411042477355034, 0.024907234119160446, 0.012787800384529636, 0.005875045729269468, 0.0024153035065944393, 0.0008885405042653874],
        },
        "q6_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00019416955659326259, 0.0004722488849771615, 0.0010135678310975295, 0.001912007135126054, 0.0031511457863129906, 0.004493585738430667, 0.005450901482574475, 0.005433818455000804, 0.004071610819132933, 0.001516700910292244] + [0.0] * 76 + [-0.001516700910292244, -0.004071610819132933, -0.005433818455000804, -0.005450901482574475, -0.004493585738430667, -0.0031511457863129906, -0.001912007135126054, -0.0010135678310975295, -0.0004722488849771615, -0.00019416955659326259],
        },
        "q6_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004395104015456173, 0.0011947131379401897, 0.0029060506472970626, 0.006325396821990164, 0.012320190713369306, 0.021472971259211725, 0.033489750539301665, 0.04673871196568297, 0.058369587576938574, 0.06522912715182705] + [0.06614140786895659] * 76 + [0.06522912715182705, 0.058369587576938574, 0.04673871196568297, 0.033489750539301665, 0.021472971259211725, 0.012320190713369306, 0.006325396821990164, 0.0029060506472970626, 0.0011947131379401897, 0.0004395104015456173],
        },
        "q6_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [9.604462528896742e-05, 0.00023359463757635204, 0.000501354302140336, 0.0009457610763755844, 0.0015586924211364315, 0.0022227210383731016, 0.002696250635611269, 0.0026878006344323957, 0.0020139940694477404, 0.0007502255923136251] + [0.0] * 76 + [-0.0007502255923136251, -0.0020139940694477404, -0.0026878006344323957, -0.002696250635611269, -0.0022227210383731016, -0.0015586924211364315, -0.0009457610763755844, -0.000501354302140336, -0.00023359463757635204, -9.604462528896742e-05],
        },
        "q6_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0004395104015456173, -0.0011947131379401897, -0.0029060506472970626, -0.006325396821990164, -0.012320190713369306, -0.021472971259211725, -0.033489750539301665, -0.04673871196568297, -0.058369587576938574, -0.06522912715182705] + [-0.06614140786895659] * 76 + [-0.06522912715182705, -0.058369587576938574, -0.04673871196568297, -0.033489750539301665, -0.021472971259211725, -0.012320190713369306, -0.006325396821990164, -0.0029060506472970626, -0.0011947131379401897, -0.0004395104015456173],
        },
        "q6_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [-9.604462528896742e-05, -0.00023359463757635204, -0.000501354302140336, -0.0009457610763755844, -0.0015586924211364315, -0.0022227210383731016, -0.002696250635611269, -0.0026878006344323957, -0.0020139940694477404, -0.0007502255923136251] + [0.0] * 76 + [0.0007502255923136251, 0.0020139940694477404, 0.0026878006344323957, 0.002696250635611269, 0.0022227210383731016, 0.0015586924211364315, 0.0009457610763755844, 0.000501354302140336, 0.00023359463757635204, 9.604462528896742e-05],
        },
        "q6_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00019456616722436429, -0.00047321350029376453, -0.0010156381442002064, -0.0019159125998643902, -0.00315758231498891, -0.004502764334225484, -0.005462035490989635, -0.005444917569633097, -0.004079927489186208, -0.0015197989227499005] + [0.0] * 76 + [0.0015197989227499005, 0.004079927489186208, 0.005444917569633097, 0.005462035490989635, 0.004502764334225484, 0.00315758231498891, 0.0019159125998643902, 0.0010156381442002064, 0.00047321350029376453, 0.00019456616722436429],
        },
        "q6_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008903554366180133, 0.002420237004228465, 0.005887046094493137, 0.012813920738667, 0.024958109622078197, 0.04349971384920038, 0.06784317585838401, 0.09468277918526134, 0.11824448169944966, 0.13214046307263333] + [0.13398855152142003] * 76 + [0.13214046307263333, 0.11824448169944966, 0.09468277918526134, 0.06784317585838401, 0.04349971384920038, 0.024958109622078197, 0.012813920738667, 0.005887046094493137, 0.002420237004228465, 0.0008903554366180133],
        },
        "q6_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [-9.604379609894118e-05, -0.00023359262086440093, -0.0005013499737566738, -0.0009457529112580738, -0.0015586789643479261, -0.0022227018487712825, -0.0026962273578471194, -0.002687777429620342, -0.0020139766818657676, -0.0007502191153288203] + [0.0] * 76 + [0.0007502191153288203, 0.0020139766818657676, 0.002687777429620342, 0.0026962273578471194, 0.0022227018487712825, 0.0015586789643479261, 0.0009457529112580738, 0.0005013499737566738, 0.00023359262086440093, 9.604379609894118e-05],
        },
        "q6_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004395066070840293, 0.0011947028235242063, 0.0029060255582490785, 0.006325342212417363, 0.012320084348445394, 0.0214727858748287, 0.03348946140946181, 0.04673830845248601, 0.058369083649938924, 0.06522856400379569] + [0.06614083684485647] * 76 + [0.06522856400379569, 0.058369083649938924, 0.04673830845248601, 0.03348946140946181, 0.0214727858748287, 0.012320084348445394, 0.006325342212417363, 0.0029060255582490785, 0.0011947028235242063, 0.0004395066070840293],
        },
        "q6_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005721838064443316, -0.0013916350705860325, -0.002986807560681391, -0.0056343514386081065, -0.009285876850666641, -0.013241813173551003, -0.01606285564830268, -0.016012514946525353, -0.01199832670850443, -0.004469452963249501] + [0.0] * 76 + [0.004469452963249501, 0.01199832670850443, 0.016012514946525353, 0.01606285564830268, 0.013241813173551003, 0.009285876850666641, 0.0056343514386081065, 0.002986807560681391, 0.0013916350705860325, 0.0005721838064443316],
        },
        "q6_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.002618373842072091, 0.0071174780350170596, 0.0173127347427056, 0.037683416640836805, 0.0733972733746041, 0.12792476823975737, 0.1995144744726272, 0.27844487955852, 0.3477355729159673, 0.3886011336134702] + [0.3940360265260349] * 76 + [0.3886011336134702, 0.3477355729159673, 0.27844487955852, 0.1995144744726272, 0.12792476823975737, 0.0733972733746041, 0.037683416640836805, 0.0173127347427056, 0.0071174780350170596, 0.002618373842072091],
        },
        "q6_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.002618373842072091, 0.0071174780350170596, 0.0173127347427056, 0.037683416640836805, 0.0733972733746041, 0.12792476823975737, 0.1995144744726272, 0.27844487955852, 0.3477355729159673, 0.3886011336134702] + [0.3940360265260349] * 76 + [0.3886011336134702, 0.3477355729159673, 0.27844487955852, 0.1995144744726272, 0.12792476823975737, 0.0733972733746041, 0.037683416640836805, 0.0173127347427056, 0.0071174780350170596, 0.002618373842072091],
        },
        "q6_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005721838064443316, 0.0013916350705860325, 0.002986807560681391, 0.0056343514386081065, 0.009285876850666641, 0.013241813173551003, 0.01606285564830268, 0.016012514946525353, 0.01199832670850443, 0.004469452963249501] + [0.0] * 76 + [-0.004469452963249501, -0.01199832670850443, -0.016012514946525353, -0.01606285564830268, -0.013241813173551003, -0.009285876850666641, -0.0056343514386081065, -0.002986807560681391, -0.0013916350705860325, -0.0005721838064443316],
        },
        "q6_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [9.604379609894118e-05, 0.00023359262086440093, 0.0005013499737566738, 0.0009457529112580738, 0.0015586789643479261, 0.0022227018487712825, 0.0026962273578471194, 0.002687777429620342, 0.0020139766818657676, 0.0007502191153288203] + [0.0] * 76 + [-0.0007502191153288203, -0.0020139766818657676, -0.002687777429620342, -0.0026962273578471194, -0.0022227018487712825, -0.0015586789643479261, -0.0009457529112580738, -0.0005013499737566738, -0.00023359262086440093, -9.604379609894118e-05],
        },
        "q6_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0004395066070840293, -0.0011947028235242063, -0.0029060255582490785, -0.006325342212417363, -0.012320084348445394, -0.0214727858748287, -0.03348946140946181, -0.04673830845248601, -0.058369083649938924, -0.06522856400379569] + [-0.06614083684485647] * 76 + [-0.06522856400379569, -0.058369083649938924, -0.04673830845248601, -0.03348946140946181, -0.0214727858748287, -0.012320084348445394, -0.006325342212417363, -0.0029060255582490785, -0.0011947028235242063, -0.0004395066070840293],
        },
        "q7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 492 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00011257974777361855+0j), (0.0003060234826255299+0j), (0.0007443793087479585+0j), (0.0016202382839710565+0j), (0.0031557932603104395+0j), (0.005500260471221883+0j), (0.008578335473875393+0j), (0.011972031573897268+0j), (0.014951258090714032+0j), (0.016708316018054+0j)] + [(0.016941994976895476+0j)] * 492 + [(0.016708316018054+0j), (0.014951258090714032+0j), (0.011972031573897268+0j), (0.008578335473875393+0j), (0.005500260471221883+0j), (0.0031557932603104395+0j), (0.0016202382839710565+0j), (0.0007443793087479585+0j), (0.0003060234826255299+0j), (0.00011257974777361855+0j)],
        },
        "q7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 492 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q7_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 492 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(5.6381512762923065e-05+0j), (0.0001532608416044855+0j), (0.0003727955722642306+0j), (0.0008114380010016118+0j), (0.0015804654167561976+0j), (0.002754607396893355+0j), (0.004296150422876324+0j), (0.005995760910205055+0j), (0.00748779923151408+0j), (0.008367758424127658+0j)] + [(0.00848478811606515+0j)] * 492 + [(0.008367758424127658+0j), (0.00748779923151408+0j), (0.005995760910205055+0j), (0.004296150422876324+0j), (0.002754607396893355+0j), (0.0015804654167561976+0j), (0.0008114380010016118+0j), (0.0003727955722642306+0j), (0.0001532608416044855+0j), (5.6381512762923065e-05+0j)],
        },
        "q7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-5.6381512762923065e-05+0j), (-0.0001532608416044855+0j), (-0.0003727955722642306+0j), (-0.0008114380010016118+0j), (-0.0015804654167561976+0j), (-0.002754607396893355+0j), (-0.004296150422876324+0j), (-0.005995760910205055+0j), (-0.00748779923151408+0j), (-0.008367758424127658+0j)] + [(-0.00848478811606515+0j)] * 492 + [(-0.008367758424127658+0j), (-0.00748779923151408+0j), (-0.005995760910205055+0j), (-0.004296150422876324+0j), (-0.002754607396893355+0j), (-0.0015804654167561976+0j), (-0.0008114380010016118+0j), (-0.0003727955722642306+0j), (-0.0001532608416044855+0j), (-5.6381512762923065e-05+0j)],
        },
        "q7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00011262973261513518+0j), (0.000306159355511923+0j), (0.0007447098094153684+0j), (0.0016209576616161932+0j), (0.0031571944166382464+0j), (0.00550270255919411+0j), (0.008582144211660099+0j), (0.011977347095673498+0j), (0.014957896374072433+0j), (0.016715734426290724+0j)] + [(0.016949517137414067+0j)] * 492 + [(0.016715734426290724+0j), (0.014957896374072433+0j), (0.011977347095673498+0j), (0.008582144211660099+0j), (0.00550270255919411+0j), (0.0031571944166382464+0j), (0.0016209576616161932+0j), (0.0007447098094153684+0j), (0.000306159355511923+0j), (0.00011262973261513518+0j)],
        },
        "q7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(5.628987388680927e-05+0j), (0.00015301174131276496+0j), (0.00037218965437397925+0j), (0.0008101191419855282+0j), (0.0015778966301552197+0j), (0.0027501302356109417+0j), (0.004289167736937697+0j), (0.005986015786948634+0j), (0.007475629045357016+0j), (0.008354158009027+0j)] + [(0.008470997488447738+0j)] * 492 + [(0.008354158009027+0j), (0.007475629045357016+0j), (0.005986015786948634+0j), (0.004289167736937697+0j), (0.0027501302356109417+0j), (0.0015778966301552197+0j), (0.0008101191419855282+0j), (0.00037218965437397925+0j), (0.00015301174131276496+0j), (5.628987388680927e-05+0j)],
        },
        "q7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-5.628987388680927e-05+0j), (-0.00015301174131276496+0j), (-0.00037218965437397925+0j), (-0.0008101191419855282+0j), (-0.0015778966301552197+0j), (-0.0027501302356109417+0j), (-0.004289167736937697+0j), (-0.005986015786948634+0j), (-0.007475629045357016+0j), (-0.008354158009027+0j)] + [(-0.008470997488447738+0j)] * 492 + [(-0.008354158009027+0j), (-0.007475629045357016+0j), (-0.005986015786948634+0j), (-0.004289167736937697+0j), (-0.0027501302356109417+0j), (-0.0015778966301552197+0j), (-0.0008101191419855282+0j), (-0.00037218965437397925+0j), (-0.00015301174131276496+0j), (-5.628987388680927e-05+0j)],
        },
        "q7_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0004149651955011534+0j), (0.0004343622069751615+0j), (0.000454561541718332+0j), (0.0004755910217072115+0j), (0.0004974791745128755+0j), (0.0005202552391485965+0j), (0.0005439491713521765+0j), (0.0005685916482694795+0j), (0.0005942140725051567+0j), (0.000620848575506051+0j), (0.0006485280202422817+0j), (0.0006772860031505917+0j), (0.0007071568553041587+0j), (0.0007381756427727404+0j), (0.0007703781661367505+0j), (0.0008038009591186315+0j), (0.0008384812862947461+0j), (0.0008744571398508864+0j), (0.000911767235344494+0j), (0.0009504510064366802+0j), (0.000990548598557279+0j), (0.0010321008614663071+0j), (0.0010751493406754849+0j), (0.00111973626769378+0j), (0.001165904549061379+0j), (0.0012136977541369505+0j), (0.0012631601016036885+0j), (0.0013143364446602654+0j), (0.0013672722548636065+0j), (0.0014220136045912449+0j), (0.0014786071480919778+0j), (0.0015371001010945887+0j), (0.0015975402189455457+0j), (0.0016599757732478479+0j), (0.001724455526974524+0j), (0.001791028708031767+0j), (0.0018597449812482166+0j), (0.0019306544187685899+0j), (0.002003807468831613+0j), (0.002079254922914089+0j), (0.0021570478812249147+0j), (0.0022372377165349403+0j), (0.0023198760363307694+0j), (0.0024050146432828654+0j), (0.002492705494020783+0j), (0.0025830006562107682+0j), (0.0026759522639336585+0j), (0.002771612471363647+0j), (0.002870033404751324+0j), (0.002971267112717275+0j), (0.00307536551486551+0j), (0.003182380348729108+0j), (0.0032923631150635463+0j), (0.003405365021506527+0j), (0.0035214369246263713+0j), (0.0036406292703844594+0j), (0.003762992033040712+0j), (0.0038885746525345525+0j), (0.004017425970377496+0j), (0.004149594164097062+0j), (0.004285126680275449+0j), (0.004424070166230155+0j), (0.004566470400387479+0j), (0.004712372221403659+0j), (0.0048618194560922185+0j), (0.005014854846219947+0j), (0.00517151997423776+0j), (0.005331855188016576+0j), (0.005495899524662148+0j), (0.005663690633486606+0j), (0.005835264698218323+0j), (0.006010656358535378+0j), (0.006189898631011701+0j), (0.006373022829568614+0j), (0.006560058485528049+0j), (0.006751033267367329+0j), (0.006945972900278813+0j), (0.007144901085641026+0j), (0.00734783942051125+0j), (0.007554807317252622+0j), (0.007765821923411856+0j), (0.007980898041966587+0j), (0.008200048052064144+0j), (0.008423281830376106+0j), (0.008650606673195494+0j), (0.008882027219405753+0j), (0.00911754537445276+0j), (0.009357160235452985+0j), (0.009600868017572787+0j), (0.009848661981815167+0j), (0.010100532364351792+0j), (0.010356466307539038+0j), (0.01061644779275778+0j), (0.010880457575217196+0j), (0.011148473120863266+0j), (0.011420468545532764+0j), (0.011696414556493402+0j), (0.01197627839651037+0j), (0.012260023790578905+0j), (0.0125476108954615+0j), (0.01283899625216716+0j), (0.013134132741508665+0j), (0.013432969542871884+0j), (0.013735452096329218+0j), (0.014041522068226746+0j), (0.0143511173203721+0j), (0.014664171882946955+0j), (0.014980615931264925+0j), (0.015300375766491934+0j), (0.015623373800442372+0j), (0.0159495285445601+0j), (0.01627875460318899+0j), (0.016610962671232896+0j), (0.016946059536299903+0j), (0.017283948085420497+0j), (0.017624527316423555+0j), (0.017967692354048354+0j), (0.018313334470864574+0j), (0.018661341113065943+0j), (0.019011595931196563+0j), (0.019363978815862017+0j), (0.019718365938470435+0j), (0.020074629797041145+0j), (0.02043263926711133+0j), (0.020792259657763056+0j), (0.021153352772785516+0j), (0.021515776976978884+0j), (0.021879387267598385+0j), (0.02224403535092835+0j), (0.022609569723968055+0j), (0.022975835761202032+0j), (0.02334267580641931+0j), (0.023709929269536956+0j), (0.02407743272837456+0j), (0.024445020035317504+0j), (0.02481252242879783+0j), (0.02517976864951269+0j), (0.025546585061291437+0j), (0.025912795776513554+0j), (0.026278222785970744+0j), (0.026642686093057866+0j), (0.027006003852168566+0j), (0.027367992511163026+0j), (0.027728466957766755+0j), (0.028087240669751014+0j), (0.028444125868737388+0j), (0.028798933677461093+0j), (0.029151474280319688+0j), (0.02950155708702655+0j), (0.029848990899181048+0j), (0.0301935840795603+0j), (0.03053514472393069+0j), (0.030873480835170858+0j), (0.03120840049949164+0j), (0.031539712064532675+0j), (0.03186722431910982+0j), (0.03219074667438249+0j), (0.032510089346205105+0j), (0.032825063538422565+0j), (0.03313548162686572+0j), (0.03344115734379898+0j), (0.03374190596256939+0j), (0.03403754448220348+0j), (0.034327891811696175+0j), (0.03461276895373386+0j), (0.034891999187592754+0j), (0.03516540825095256+0j), (0.035432824520364815+0j), (0.03569407919011589+0j), (0.03594900644922451+0j), (0.03619744365631504+0j), (0.036439231512109274+0j), (0.03667421422928117+0j), (0.03690223969942172+0j), (0.03712315965686395+0j), (0.037336829839121406+0j), (0.03754311014369757+0j), (0.03774186478102777+0j), (0.037932962423320234+0j), (0.038116276349067994+0j), (0.038291684583009286+0j), (0.03845907003132011+0j), (0.03861832061182935+0j), (0.03876932937905377+0j), (0.03891199464385774+0j), (0.039046220087550265+0j), (0.03917191487024018+0j), (0.03928899373327889+0j), (0.03939737709562892+0j), (0.03949699114400586+0j), (0.03958776791665071+0j), (0.03966964538059961+0j), (0.039742567502327894+0j), (0.03980648431165596+0j), (0.039861351958814774+0j), (0.039907132764579925+0j), (0.03994379526339395+0j), (0.039971314239407744+0j), (0.03998967075538343+0j), (0.03999885217441219+0j)] + [(0.04000000000000001+0j)] * 2800 + [(0.03999885217441219+0j), (0.03998967075538343+0j), (0.039971314239407744+0j), (0.03994379526339395+0j), (0.039907132764579925+0j), (0.039861351958814774+0j), (0.03980648431165596+0j), (0.039742567502327894+0j), (0.03966964538059961+0j), (0.03958776791665071+0j), (0.03949699114400586+0j), (0.03939737709562892+0j), (0.03928899373327889+0j), (0.03917191487024018+0j), (0.039046220087550265+0j), (0.03891199464385774+0j), (0.03876932937905377+0j), (0.03861832061182935+0j), (0.03845907003132011+0j), (0.038291684583009286+0j), (0.038116276349067994+0j), (0.037932962423320234+0j), (0.03774186478102777+0j), (0.03754311014369757+0j), (0.037336829839121406+0j), (0.03712315965686395+0j), (0.03690223969942172+0j), (0.03667421422928117+0j), (0.036439231512109274+0j), (0.03619744365631504+0j), (0.03594900644922451+0j), (0.03569407919011589+0j), (0.035432824520364815+0j), (0.03516540825095256+0j), (0.034891999187592754+0j), (0.03461276895373386+0j), (0.034327891811696175+0j), (0.03403754448220348+0j), (0.03374190596256939+0j), (0.03344115734379898+0j), (0.03313548162686572+0j), (0.032825063538422565+0j), (0.032510089346205105+0j), (0.03219074667438249+0j), (0.03186722431910982+0j), (0.031539712064532675+0j), (0.03120840049949164+0j), (0.030873480835170858+0j), (0.03053514472393069+0j), (0.0301935840795603+0j), (0.029848990899181048+0j), (0.02950155708702655+0j), (0.029151474280319688+0j), (0.028798933677461093+0j), (0.028444125868737388+0j), (0.028087240669751014+0j), (0.027728466957766755+0j), (0.027367992511163026+0j), (0.027006003852168566+0j), (0.026642686093057866+0j), (0.026278222785970744+0j), (0.025912795776513554+0j), (0.025546585061291437+0j), (0.02517976864951269+0j), (0.02481252242879783+0j), (0.024445020035317504+0j), (0.02407743272837456+0j), (0.023709929269536956+0j), (0.02334267580641931+0j), (0.022975835761202032+0j), (0.022609569723968055+0j), (0.02224403535092835+0j), (0.021879387267598385+0j), (0.021515776976978884+0j), (0.021153352772785516+0j), (0.020792259657763056+0j), (0.02043263926711133+0j), (0.020074629797041145+0j), (0.019718365938470435+0j), (0.019363978815862017+0j), (0.019011595931196563+0j), (0.018661341113065943+0j), (0.018313334470864574+0j), (0.017967692354048354+0j), (0.017624527316423555+0j), (0.017283948085420497+0j), (0.016946059536299903+0j), (0.016610962671232896+0j), (0.01627875460318899+0j), (0.0159495285445601+0j), (0.015623373800442372+0j), (0.015300375766491934+0j), (0.014980615931264925+0j), (0.014664171882946955+0j), (0.0143511173203721+0j), (0.014041522068226746+0j), (0.013735452096329218+0j), (0.013432969542871884+0j), (0.013134132741508665+0j), (0.01283899625216716+0j), (0.0125476108954615+0j), (0.012260023790578905+0j), (0.01197627839651037+0j), (0.011696414556493402+0j), (0.011420468545532764+0j), (0.011148473120863266+0j), (0.010880457575217196+0j), (0.01061644779275778+0j), (0.010356466307539038+0j), (0.010100532364351792+0j), (0.009848661981815167+0j), (0.009600868017572787+0j), (0.009357160235452985+0j), (0.00911754537445276+0j), (0.008882027219405753+0j), (0.008650606673195494+0j), (0.008423281830376106+0j), (0.008200048052064144+0j), (0.007980898041966587+0j), (0.007765821923411856+0j), (0.007554807317252622+0j), (0.00734783942051125+0j), (0.007144901085641026+0j), (0.006945972900278813+0j), (0.006751033267367329+0j), (0.006560058485528049+0j), (0.006373022829568614+0j), (0.006189898631011701+0j), (0.006010656358535378+0j), (0.005835264698218323+0j), (0.005663690633486606+0j), (0.005495899524662148+0j), (0.005331855188016576+0j), (0.00517151997423776+0j), (0.005014854846219947+0j), (0.0048618194560922185+0j), (0.004712372221403659+0j), (0.004566470400387479+0j), (0.004424070166230155+0j), (0.004285126680275449+0j), (0.004149594164097062+0j), (0.004017425970377496+0j), (0.0038885746525345525+0j), (0.003762992033040712+0j), (0.0036406292703844594+0j), (0.0035214369246263713+0j), (0.003405365021506527+0j), (0.0032923631150635463+0j), (0.003182380348729108+0j), (0.00307536551486551+0j), (0.002971267112717275+0j), (0.002870033404751324+0j), (0.002771612471363647+0j), (0.0026759522639336585+0j), (0.0025830006562107682+0j), (0.002492705494020783+0j), (0.0024050146432828654+0j), (0.0023198760363307694+0j), (0.0022372377165349403+0j), (0.0021570478812249147+0j), (0.002079254922914089+0j), (0.002003807468831613+0j), (0.0019306544187685899+0j), (0.0018597449812482166+0j), (0.001791028708031767+0j), (0.001724455526974524+0j), (0.0016599757732478479+0j), (0.0015975402189455457+0j), (0.0015371001010945887+0j), (0.0014786071480919778+0j), (0.0014220136045912449+0j), (0.0013672722548636065+0j), (0.0013143364446602654+0j), (0.0012631601016036885+0j), (0.0012136977541369505+0j), (0.001165904549061379+0j), (0.00111973626769378+0j), (0.0010751493406754849+0j), (0.0010321008614663071+0j), (0.000990548598557279+0j), (0.0009504510064366802+0j), (0.000911767235344494+0j), (0.0008744571398508864+0j), (0.0008384812862947461+0j), (0.0008038009591186315+0j), (0.0007703781661367505+0j), (0.0007381756427727404+0j), (0.0007071568553041587+0j), (0.0006772860031505917+0j), (0.0006485280202422817+0j), (0.000620848575506051+0j), (0.0005942140725051567+0j), (0.0005685916482694795+0j), (0.0005439491713521765+0j), (0.0005202552391485965+0j), (0.0004974791745128755+0j), (0.0004755910217072115+0j), (0.000454561541718332+0j), (0.0004343622069751615+0j), (0.0004149651955011534+0j)],
        },
        "q7_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.00011257974777361855, 0.0003060234826255299, 0.0007443793087479585, 0.0016202382839710565, 0.0031557932603104395, 0.005500260471221883, 0.008578335473875393, 0.011972031573897268, 0.014951258090714032, 0.016708316018054] + [0.016941994976895476] * 492 + [0.016708316018054, 0.014951258090714032, 0.011972031573897268, 0.008578335473875393, 0.005500260471221883, 0.0031557932603104395, 0.0016202382839710565, 0.0007443793087479585, 0.0003060234826255299, 0.00011257974777361855],
        },
        "q7_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-6.989351536890887e-05, -0.00016999129667501453, -0.00036484513856434764, -0.000688248469168278, -0.0011342903610100825, -0.0016175167177644545, -0.0019621132850645186, -0.0019559640571875187, -0.0014656221003759447, -0.00054595354824654] + [0.0] * 492 + [0.00054595354824654, 0.0014656221003759447, 0.0019559640571875187, 0.0019621132850645186, 0.0016175167177644545, 0.0011342903610100825, 0.000688248469168278, 0.00036484513856434764, 0.00016999129667501453, 6.989351536890887e-05],
        },
        "q7_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [5.6381512762923065e-05, 0.0001532608416044855, 0.0003727955722642306, 0.0008114380010016118, 0.0015804654167561976, 0.002754607396893355, 0.004296150422876324, 0.005995760910205055, 0.00748779923151408, 0.008367758424127658] + [0.00848478811606515] * 492 + [0.008367758424127658, 0.00748779923151408, 0.005995760910205055, 0.004296150422876324, 0.002754607396893355, 0.0015804654167561976, 0.0008114380010016118, 0.0003727955722642306, 0.0001532608416044855, 5.6381512762923065e-05],
        },
        "q7_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-3.5003650361181064e-05, -8.513401968479211e-05, -0.0001827195498591853, -0.0003446844624887924, -0.0005680684823948154, -0.0008100750025685256, -0.0009826537846453576, -0.0009795741652920942, -0.0007340040530569791, -0.00027342117527499627] + [0.0] * 492 + [0.00027342117527499627, 0.0007340040530569791, 0.0009795741652920942, 0.0009826537846453576, 0.0008100750025685256, 0.0005680684823948154, 0.0003446844624887924, 0.0001827195498591853, 8.513401968479211e-05, 3.5003650361181064e-05],
        },
        "q7_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-5.6381512762923065e-05, -0.0001532608416044855, -0.0003727955722642306, -0.0008114380010016118, -0.0015804654167561976, -0.002754607396893355, -0.004296150422876324, -0.005995760910205055, -0.00748779923151408, -0.008367758424127658] + [-0.00848478811606515] * 492 + [-0.008367758424127658, -0.00748779923151408, -0.005995760910205055, -0.004296150422876324, -0.002754607396893355, -0.0015804654167561976, -0.0008114380010016118, -0.0003727955722642306, -0.0001532608416044855, -5.6381512762923065e-05],
        },
        "q7_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [3.5003650361181064e-05, 8.513401968479211e-05, 0.0001827195498591853, 0.0003446844624887924, 0.0005680684823948154, 0.0008100750025685256, 0.0009826537846453576, 0.0009795741652920942, 0.0007340040530569791, 0.00027342117527499627] + [0.0] * 492 + [-0.00027342117527499627, -0.0007340040530569791, -0.0009795741652920942, -0.0009826537846453576, -0.0008100750025685256, -0.0005680684823948154, -0.0003446844624887924, -0.0001827195498591853, -8.513401968479211e-05, -3.5003650361181064e-05],
        },
        "q7_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [6.99245477380325e-05, 0.00017006677195535174, 0.00036500712796999033, 0.0006885540480253618, 0.001134793980222687, 0.0016182348870478903, 0.001962984453489845, 0.001956832495386611, 0.0014662728292135848, 0.0005461959488747543] + [0.0] * 492 + [-0.0005461959488747543, -0.0014662728292135848, -0.001956832495386611, -0.001962984453489845, -0.0016182348870478903, -0.001134793980222687, -0.0006885540480253618, -0.00036500712796999033, -0.00017006677195535174, -6.99245477380325e-05],
        },
        "q7_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00011262973261513518, 0.000306159355511923, 0.0007447098094153684, 0.0016209576616161932, 0.0031571944166382464, 0.00550270255919411, 0.008582144211660099, 0.011977347095673498, 0.014957896374072433, 0.016715734426290724] + [0.016949517137414067] * 492 + [0.016715734426290724, 0.014957896374072433, 0.011977347095673498, 0.008582144211660099, 0.00550270255919411, 0.0031571944166382464, 0.0016209576616161932, 0.0007447098094153684, 0.000306159355511923, 0.00011262973261513518],
        },
        "q7_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [3.494675768445444e-05, 8.499564833750727e-05, 0.00018242256928217382, 0.000344124234584139, 0.0005671451805050413, 0.0008087583588822272, 0.0009810566425322593, 0.0009779820285937594, 0.0007328110501879724, 0.00027297677412327] + [0.0] * 492 + [-0.00027297677412327, -0.0007328110501879724, -0.0009779820285937594, -0.0009810566425322593, -0.0008087583588822272, -0.0005671451805050413, -0.000344124234584139, -0.00018242256928217382, -8.499564833750727e-05, -3.494675768445444e-05],
        },
        "q7_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [5.628987388680927e-05, 0.00015301174131276496, 0.00037218965437397925, 0.0008101191419855282, 0.0015778966301552197, 0.0027501302356109417, 0.004289167736937697, 0.005986015786948634, 0.007475629045357016, 0.008354158009027] + [0.008470997488447738] * 492 + [0.008354158009027, 0.007475629045357016, 0.005986015786948634, 0.004289167736937697, 0.0027501302356109417, 0.0015778966301552197, 0.0008101191419855282, 0.00037218965437397925, 0.00015301174131276496, 5.628987388680927e-05],
        },
        "q7_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00038490806108277463, 0.0009361529472193725, 0.0020092255216962282, 0.0037902283554132428, 0.006246609592561508, 0.008907768057129978, 0.010805483401324121, 0.01077161920996389, 0.008071274680608118, 0.003006601121544322] + [0.0] * 492 + [-0.003006601121544322, -0.008071274680608118, -0.01077161920996389, -0.010805483401324121, -0.008907768057129978, -0.006246609592561508, -0.0037902283554132428, -0.0020092255216962282, -0.0009361529472193725, -0.00038490806108277463],
        },
        "q7_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 492 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q7_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 492 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q7_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00038490806108277463, -0.0009361529472193725, -0.0020092255216962282, -0.0037902283554132428, -0.006246609592561508, -0.008907768057129978, -0.010805483401324121, -0.01077161920996389, -0.008071274680608118, -0.003006601121544322] + [0.0] * 492 + [0.003006601121544322, 0.008071274680608118, 0.01077161920996389, 0.010805483401324121, 0.008907768057129978, 0.006246609592561508, 0.0037902283554132428, 0.0020092255216962282, 0.0009361529472193725, 0.00038490806108277463],
        },
        "q7_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-3.494675768445444e-05, -8.499564833750727e-05, -0.00018242256928217382, -0.000344124234584139, -0.0005671451805050413, -0.0008087583588822272, -0.0009810566425322593, -0.0009779820285937594, -0.0007328110501879724, -0.00027297677412327] + [0.0] * 492 + [0.00027297677412327, 0.0007328110501879724, 0.0009779820285937594, 0.0009810566425322593, 0.0008087583588822272, 0.0005671451805050413, 0.000344124234584139, 0.00018242256928217382, 8.499564833750727e-05, 3.494675768445444e-05],
        },
        "q7_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-5.628987388680927e-05, -0.00015301174131276496, -0.00037218965437397925, -0.0008101191419855282, -0.0015778966301552197, -0.0027501302356109417, -0.004289167736937697, -0.005986015786948634, -0.007475629045357016, -0.008354158009027] + [-0.008470997488447738] * 492 + [-0.008354158009027, -0.007475629045357016, -0.005986015786948634, -0.004289167736937697, -0.0027501302356109417, -0.0015778966301552197, -0.0008101191419855282, -0.00037218965437397925, -0.00015301174131276496, -5.628987388680927e-05],
        },
        "q8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 280 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 280 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 280 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q8_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 280 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 280 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 280 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "q8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 280 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 280 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 280 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "q8_ro_wf": {
            "type": "arbitrary",
            "samples": [(0.0004149651955011534+0j), (0.0004343622069751615+0j), (0.000454561541718332+0j), (0.0004755910217072115+0j), (0.0004974791745128755+0j), (0.0005202552391485965+0j), (0.0005439491713521765+0j), (0.0005685916482694795+0j), (0.0005942140725051567+0j), (0.000620848575506051+0j), (0.0006485280202422817+0j), (0.0006772860031505917+0j), (0.0007071568553041587+0j), (0.0007381756427727404+0j), (0.0007703781661367505+0j), (0.0008038009591186315+0j), (0.0008384812862947461+0j), (0.0008744571398508864+0j), (0.000911767235344494+0j), (0.0009504510064366802+0j), (0.000990548598557279+0j), (0.0010321008614663071+0j), (0.0010751493406754849+0j), (0.00111973626769378+0j), (0.001165904549061379+0j), (0.0012136977541369505+0j), (0.0012631601016036885+0j), (0.0013143364446602654+0j), (0.0013672722548636065+0j), (0.0014220136045912449+0j), (0.0014786071480919778+0j), (0.0015371001010945887+0j), (0.0015975402189455457+0j), (0.0016599757732478479+0j), (0.001724455526974524+0j), (0.001791028708031767+0j), (0.0018597449812482166+0j), (0.0019306544187685899+0j), (0.002003807468831613+0j), (0.002079254922914089+0j), (0.0021570478812249147+0j), (0.0022372377165349403+0j), (0.0023198760363307694+0j), (0.0024050146432828654+0j), (0.002492705494020783+0j), (0.0025830006562107682+0j), (0.0026759522639336585+0j), (0.002771612471363647+0j), (0.002870033404751324+0j), (0.002971267112717275+0j), (0.00307536551486551+0j), (0.003182380348729108+0j), (0.0032923631150635463+0j), (0.003405365021506527+0j), (0.0035214369246263713+0j), (0.0036406292703844594+0j), (0.003762992033040712+0j), (0.0038885746525345525+0j), (0.004017425970377496+0j), (0.004149594164097062+0j), (0.004285126680275449+0j), (0.004424070166230155+0j), (0.004566470400387479+0j), (0.004712372221403659+0j), (0.0048618194560922185+0j), (0.005014854846219947+0j), (0.00517151997423776+0j), (0.005331855188016576+0j), (0.005495899524662148+0j), (0.005663690633486606+0j), (0.005835264698218323+0j), (0.006010656358535378+0j), (0.006189898631011701+0j), (0.006373022829568614+0j), (0.006560058485528049+0j), (0.006751033267367329+0j), (0.006945972900278813+0j), (0.007144901085641026+0j), (0.00734783942051125+0j), (0.007554807317252622+0j), (0.007765821923411856+0j), (0.007980898041966587+0j), (0.008200048052064144+0j), (0.008423281830376106+0j), (0.008650606673195494+0j), (0.008882027219405753+0j), (0.00911754537445276+0j), (0.009357160235452985+0j), (0.009600868017572787+0j), (0.009848661981815167+0j), (0.010100532364351792+0j), (0.010356466307539038+0j), (0.01061644779275778+0j), (0.010880457575217196+0j), (0.011148473120863266+0j), (0.011420468545532764+0j), (0.011696414556493402+0j), (0.01197627839651037+0j), (0.012260023790578905+0j), (0.0125476108954615+0j), (0.01283899625216716+0j), (0.013134132741508665+0j), (0.013432969542871884+0j), (0.013735452096329218+0j), (0.014041522068226746+0j), (0.0143511173203721+0j), (0.014664171882946955+0j), (0.014980615931264925+0j), (0.015300375766491934+0j), (0.015623373800442372+0j), (0.0159495285445601+0j), (0.01627875460318899+0j), (0.016610962671232896+0j), (0.016946059536299903+0j), (0.017283948085420497+0j), (0.017624527316423555+0j), (0.017967692354048354+0j), (0.018313334470864574+0j), (0.018661341113065943+0j), (0.019011595931196563+0j), (0.019363978815862017+0j), (0.019718365938470435+0j), (0.020074629797041145+0j), (0.02043263926711133+0j), (0.020792259657763056+0j), (0.021153352772785516+0j), (0.021515776976978884+0j), (0.021879387267598385+0j), (0.02224403535092835+0j), (0.022609569723968055+0j), (0.022975835761202032+0j), (0.02334267580641931+0j), (0.023709929269536956+0j), (0.02407743272837456+0j), (0.024445020035317504+0j), (0.02481252242879783+0j), (0.02517976864951269+0j), (0.025546585061291437+0j), (0.025912795776513554+0j), (0.026278222785970744+0j), (0.026642686093057866+0j), (0.027006003852168566+0j), (0.027367992511163026+0j), (0.027728466957766755+0j), (0.028087240669751014+0j), (0.028444125868737388+0j), (0.028798933677461093+0j), (0.029151474280319688+0j), (0.02950155708702655+0j), (0.029848990899181048+0j), (0.0301935840795603+0j), (0.03053514472393069+0j), (0.030873480835170858+0j), (0.03120840049949164+0j), (0.031539712064532675+0j), (0.03186722431910982+0j), (0.03219074667438249+0j), (0.032510089346205105+0j), (0.032825063538422565+0j), (0.03313548162686572+0j), (0.03344115734379898+0j), (0.03374190596256939+0j), (0.03403754448220348+0j), (0.034327891811696175+0j), (0.03461276895373386+0j), (0.034891999187592754+0j), (0.03516540825095256+0j), (0.035432824520364815+0j), (0.03569407919011589+0j), (0.03594900644922451+0j), (0.03619744365631504+0j), (0.036439231512109274+0j), (0.03667421422928117+0j), (0.03690223969942172+0j), (0.03712315965686395+0j), (0.037336829839121406+0j), (0.03754311014369757+0j), (0.03774186478102777+0j), (0.037932962423320234+0j), (0.038116276349067994+0j), (0.038291684583009286+0j), (0.03845907003132011+0j), (0.03861832061182935+0j), (0.03876932937905377+0j), (0.03891199464385774+0j), (0.039046220087550265+0j), (0.03917191487024018+0j), (0.03928899373327889+0j), (0.03939737709562892+0j), (0.03949699114400586+0j), (0.03958776791665071+0j), (0.03966964538059961+0j), (0.039742567502327894+0j), (0.03980648431165596+0j), (0.039861351958814774+0j), (0.039907132764579925+0j), (0.03994379526339395+0j), (0.039971314239407744+0j), (0.03998967075538343+0j), (0.03999885217441219+0j)] + [(0.04000000000000001+0j)] * 1600 + [(0.03999885217441219+0j), (0.03998967075538343+0j), (0.039971314239407744+0j), (0.03994379526339395+0j), (0.039907132764579925+0j), (0.039861351958814774+0j), (0.03980648431165596+0j), (0.039742567502327894+0j), (0.03966964538059961+0j), (0.03958776791665071+0j), (0.03949699114400586+0j), (0.03939737709562892+0j), (0.03928899373327889+0j), (0.03917191487024018+0j), (0.039046220087550265+0j), (0.03891199464385774+0j), (0.03876932937905377+0j), (0.03861832061182935+0j), (0.03845907003132011+0j), (0.038291684583009286+0j), (0.038116276349067994+0j), (0.037932962423320234+0j), (0.03774186478102777+0j), (0.03754311014369757+0j), (0.037336829839121406+0j), (0.03712315965686395+0j), (0.03690223969942172+0j), (0.03667421422928117+0j), (0.036439231512109274+0j), (0.03619744365631504+0j), (0.03594900644922451+0j), (0.03569407919011589+0j), (0.035432824520364815+0j), (0.03516540825095256+0j), (0.034891999187592754+0j), (0.03461276895373386+0j), (0.034327891811696175+0j), (0.03403754448220348+0j), (0.03374190596256939+0j), (0.03344115734379898+0j), (0.03313548162686572+0j), (0.032825063538422565+0j), (0.032510089346205105+0j), (0.03219074667438249+0j), (0.03186722431910982+0j), (0.031539712064532675+0j), (0.03120840049949164+0j), (0.030873480835170858+0j), (0.03053514472393069+0j), (0.0301935840795603+0j), (0.029848990899181048+0j), (0.02950155708702655+0j), (0.029151474280319688+0j), (0.028798933677461093+0j), (0.028444125868737388+0j), (0.028087240669751014+0j), (0.027728466957766755+0j), (0.027367992511163026+0j), (0.027006003852168566+0j), (0.026642686093057866+0j), (0.026278222785970744+0j), (0.025912795776513554+0j), (0.025546585061291437+0j), (0.02517976864951269+0j), (0.02481252242879783+0j), (0.024445020035317504+0j), (0.02407743272837456+0j), (0.023709929269536956+0j), (0.02334267580641931+0j), (0.022975835761202032+0j), (0.022609569723968055+0j), (0.02224403535092835+0j), (0.021879387267598385+0j), (0.021515776976978884+0j), (0.021153352772785516+0j), (0.020792259657763056+0j), (0.02043263926711133+0j), (0.020074629797041145+0j), (0.019718365938470435+0j), (0.019363978815862017+0j), (0.019011595931196563+0j), (0.018661341113065943+0j), (0.018313334470864574+0j), (0.017967692354048354+0j), (0.017624527316423555+0j), (0.017283948085420497+0j), (0.016946059536299903+0j), (0.016610962671232896+0j), (0.01627875460318899+0j), (0.0159495285445601+0j), (0.015623373800442372+0j), (0.015300375766491934+0j), (0.014980615931264925+0j), (0.014664171882946955+0j), (0.0143511173203721+0j), (0.014041522068226746+0j), (0.013735452096329218+0j), (0.013432969542871884+0j), (0.013134132741508665+0j), (0.01283899625216716+0j), (0.0125476108954615+0j), (0.012260023790578905+0j), (0.01197627839651037+0j), (0.011696414556493402+0j), (0.011420468545532764+0j), (0.011148473120863266+0j), (0.010880457575217196+0j), (0.01061644779275778+0j), (0.010356466307539038+0j), (0.010100532364351792+0j), (0.009848661981815167+0j), (0.009600868017572787+0j), (0.009357160235452985+0j), (0.00911754537445276+0j), (0.008882027219405753+0j), (0.008650606673195494+0j), (0.008423281830376106+0j), (0.008200048052064144+0j), (0.007980898041966587+0j), (0.007765821923411856+0j), (0.007554807317252622+0j), (0.00734783942051125+0j), (0.007144901085641026+0j), (0.006945972900278813+0j), (0.006751033267367329+0j), (0.006560058485528049+0j), (0.006373022829568614+0j), (0.006189898631011701+0j), (0.006010656358535378+0j), (0.005835264698218323+0j), (0.005663690633486606+0j), (0.005495899524662148+0j), (0.005331855188016576+0j), (0.00517151997423776+0j), (0.005014854846219947+0j), (0.0048618194560922185+0j), (0.004712372221403659+0j), (0.004566470400387479+0j), (0.004424070166230155+0j), (0.004285126680275449+0j), (0.004149594164097062+0j), (0.004017425970377496+0j), (0.0038885746525345525+0j), (0.003762992033040712+0j), (0.0036406292703844594+0j), (0.0035214369246263713+0j), (0.003405365021506527+0j), (0.0032923631150635463+0j), (0.003182380348729108+0j), (0.00307536551486551+0j), (0.002971267112717275+0j), (0.002870033404751324+0j), (0.002771612471363647+0j), (0.0026759522639336585+0j), (0.0025830006562107682+0j), (0.002492705494020783+0j), (0.0024050146432828654+0j), (0.0023198760363307694+0j), (0.0022372377165349403+0j), (0.0021570478812249147+0j), (0.002079254922914089+0j), (0.002003807468831613+0j), (0.0019306544187685899+0j), (0.0018597449812482166+0j), (0.001791028708031767+0j), (0.001724455526974524+0j), (0.0016599757732478479+0j), (0.0015975402189455457+0j), (0.0015371001010945887+0j), (0.0014786071480919778+0j), (0.0014220136045912449+0j), (0.0013672722548636065+0j), (0.0013143364446602654+0j), (0.0012631601016036885+0j), (0.0012136977541369505+0j), (0.001165904549061379+0j), (0.00111973626769378+0j), (0.0010751493406754849+0j), (0.0010321008614663071+0j), (0.000990548598557279+0j), (0.0009504510064366802+0j), (0.000911767235344494+0j), (0.0008744571398508864+0j), (0.0008384812862947461+0j), (0.0008038009591186315+0j), (0.0007703781661367505+0j), (0.0007381756427727404+0j), (0.0007071568553041587+0j), (0.0006772860031505917+0j), (0.0006485280202422817+0j), (0.000620848575506051+0j), (0.0005942140725051567+0j), (0.0005685916482694795+0j), (0.0005439491713521765+0j), (0.0005202552391485965+0j), (0.0004974791745128755+0j), (0.0004755910217072115+0j), (0.000454561541718332+0j), (0.0004343622069751615+0j), (0.0004149651955011534+0j)],
        },
        "q8_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
        },
        "q8_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006060349618751102, -0.0014739660532995628, -0.003163511070706866, -0.005967687167707441, -0.009835241682461419, -0.014025216462624716, -0.01701315556432408, -0.01695983663963802, -0.012708163683519139, -0.004733871748341827] + [0.0] * 280 + [0.004733871748341827, 0.012708163683519139, 0.01695983663963802, 0.01701315556432408, 0.014025216462624716, 0.009835241682461419, 0.005967687167707441, 0.003163511070706866, 0.0014739660532995628, 0.0006060349618751102],
        },
        "q8_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
        },
        "q8_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00027510759179523057, -0.0006691020763167246, -0.0014360655193669622, -0.0027090121009117987, -0.004464675842486502, -0.006366701210605477, -0.00772306640801254, -0.007698862456276641, -0.005768829402672357, -0.002148925620601698] + [0.0] * 280 + [0.002148925620601698, 0.005768829402672357, 0.007698862456276641, 0.00772306640801254, 0.006366701210605477, 0.004464675842486502, 0.0027090121009117987, 0.0014360655193669622, 0.0006691020763167246, 0.00027510759179523057],
        },
        "q8_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
        },
        "q8_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00027510759179523057, 0.0006691020763167246, 0.0014360655193669622, 0.0027090121009117987, 0.004464675842486502, 0.006366701210605477, 0.00772306640801254, 0.007698862456276641, 0.005768829402672357, 0.002148925620601698] + [0.0] * 280 + [-0.002148925620601698, -0.005768829402672357, -0.007698862456276641, -0.00772306640801254, -0.006366701210605477, -0.004464675842486502, -0.0027090121009117987, -0.0014360655193669622, -0.0006691020763167246, -0.00027510759179523057],
        },
        "q8_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006060349618751102, 0.0014739660532995628, 0.003163511070706866, 0.005967687167707441, 0.009835241682461419, 0.014025216462624716, 0.01701315556432408, 0.01695983663963802, 0.012708163683519139, 0.004733871748341827] + [0.0] * 280 + [-0.004733871748341827, -0.012708163683519139, -0.01695983663963802, -0.01701315556432408, -0.014025216462624716, -0.009835241682461419, -0.005967687167707441, -0.003163511070706866, -0.0014739660532995628, -0.0006060349618751102],
        },
        "q8_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
        },
        "q8_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00027510759179523057, 0.0006691020763167246, 0.0014360655193669622, 0.0027090121009117987, 0.004464675842486502, 0.006366701210605477, 0.00772306640801254, 0.007698862456276641, 0.005768829402672357, 0.002148925620601698] + [0.0] * 280 + [-0.002148925620601698, -0.005768829402672357, -0.007698862456276641, -0.00772306640801254, -0.006366701210605477, -0.004464675842486502, -0.0027090121009117987, -0.0014360655193669622, -0.0006691020763167246, -0.00027510759179523057],
        },
        "q8_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
        },
        "q8_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00038490806108277463, 0.0009361529472193725, 0.0020092255216962282, 0.0037902283554132428, 0.006246609592561508, 0.008907768057129978, 0.010805483401324121, 0.01077161920996389, 0.008071274680608118, 0.003006601121544322] + [0.0] * 280 + [-0.003006601121544322, -0.008071274680608118, -0.01077161920996389, -0.010805483401324121, -0.008907768057129978, -0.006246609592561508, -0.0037902283554132428, -0.0020092255216962282, -0.0009361529472193725, -0.00038490806108277463],
        },
        "q8_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q8_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
        },
        "q8_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00038490806108277463, -0.0009361529472193725, -0.0020092255216962282, -0.0037902283554132428, -0.006246609592561508, -0.008907768057129978, -0.010805483401324121, -0.01077161920996389, -0.008071274680608118, -0.003006601121544322] + [0.0] * 280 + [0.003006601121544322, 0.008071274680608118, 0.01077161920996389, 0.010805483401324121, 0.008907768057129978, 0.006246609592561508, 0.0037902283554132428, 0.0020092255216962282, 0.0009361529472193725, 0.00038490806108277463],
        },
        "q8_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00027510759179523057, -0.0006691020763167246, -0.0014360655193669622, -0.0027090121009117987, -0.004464675842486502, -0.006366701210605477, -0.00772306640801254, -0.007698862456276641, -0.005768829402672357, -0.002148925620601698] + [0.0] * 280 + [0.002148925620601698, 0.005768829402672357, 0.007698862456276641, 0.00772306640801254, 0.006366701210605477, 0.004464675842486502, 0.0027090121009117987, 0.0014360655193669622, 0.0006691020763167246, 0.00027510759179523057],
        },
        "q8_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
        },
        "rise_wf": {
            "type": "arbitrary",
            "samples": [0.0032754804057496334, 0.005968314427627137, 0.010448563941567294, 0.01757477344936297, 0.028402141495854794, 0.04410021012179409, 0.06578978263086196, 0.09429843062234541, 0.1298609869433399, 0.17182294328429568, 0.21842977065588376, 0.26679072434338974, 0.3130818152967473, 0.3529987610338382, 0.38239899273324, 0.39800499167707293],
        },
        "fall_wf": {
            "type": "arbitrary",
            "samples": [0.39800499167707293, 0.38239899273324, 0.3529987610338382, 0.3130818152967473, 0.26679072434338974, 0.21842977065588376, 0.17182294328429568, 0.1298609869433399, 0.09429843062234541, 0.06578978263086196, 0.04410021012179409, 0.028402141495854794, 0.01757477344936297, 0.010448563941567294, 0.005968314427627137, 0.0032754804057496334],
        },
        "q12_1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0008247924959848904+0j), (0.0022420184540851078+0j), (0.005453542756698274+0j), (0.011870344398123803+0j), (0.02312027386326841+0j), (0.04029653336716045+0j), (0.06284742031151912+0j), (0.08771064067136396+0j), (0.10953733440184583+0j), (0.12241005993321687+0j)] + [(0.12412206103051526+0j)] * 32 + [(0.12241005993321687+0j), (0.10953733440184583+0j), (0.08771064067136396+0j), (0.06284742031151912+0j), (0.04029653336716045+0j), (0.02312027386326841+0j), (0.011870344398123803+0j), (0.005453542756698274+0j), (0.0022420184540851078+0j), (0.0008247924959848904+0j)],
        },
        "q12_1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0003685439935695536+0j), (0.0010018064407078446+0j), (0.002436819486646631+0j), (0.005304054232824478+0j), (0.01033088698487238+0j), (0.018005795889799343+0j), (0.028082262362842645+0j), (0.03919195427811065+0j), (0.04894482777418412+0j), (0.054696778353937145+0j)] + [(0.05546175587793897+0j)] * 32 + [(0.054696778353937145+0j), (0.04894482777418412+0j), (0.03919195427811065+0j), (0.028082262362842645+0j), (0.018005795889799343+0j), (0.01033088698487238+0j), (0.005304054232824478+0j), (0.002436819486646631+0j), (0.0010018064407078446+0j), (0.0003685439935695536+0j)],
        },
        "q12_1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0003685439935695536+0j), (-0.0010018064407078446+0j), (-0.002436819486646631+0j), (-0.005304054232824478+0j), (-0.01033088698487238+0j), (-0.018005795889799343+0j), (-0.028082262362842645+0j), (-0.03919195427811065+0j), (-0.04894482777418412+0j), (-0.054696778353937145+0j)] + [(-0.05546175587793897+0j)] * 32 + [(-0.054696778353937145+0j), (-0.04894482777418412+0j), (-0.03919195427811065+0j), (-0.028082262362842645+0j), (-0.018005795889799343+0j), (-0.01033088698487238+0j), (-0.005304054232824478+0j), (-0.002436819486646631+0j), (-0.0010018064407078446+0j), (-0.0003685439935695536+0j)],
        },
        "q12_1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0008247924959848904+0j), (0.0022420184540851078+0j), (0.005453542756698274+0j), (0.011870344398123803+0j), (0.02312027386326841+0j), (0.04029653336716045+0j), (0.06284742031151912+0j), (0.08771064067136396+0j), (0.10953733440184583+0j), (0.12241005993321687+0j)] + [(0.12412206103051526+0j)] * 32 + [(0.12241005993321687+0j), (0.10953733440184583+0j), (0.08771064067136396+0j), (0.06284742031151912+0j), (0.04029653336716045+0j), (0.02312027386326841+0j), (0.011870344398123803+0j), (0.005453542756698274+0j), (0.0022420184540851078+0j), (0.0008247924959848904+0j)],
        },
        "q12_1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0003685439935695536+0j), (0.0010018064407078446+0j), (0.002436819486646631+0j), (0.005304054232824478+0j), (0.01033088698487238+0j), (0.018005795889799343+0j), (0.028082262362842645+0j), (0.03919195427811065+0j), (0.04894482777418412+0j), (0.054696778353937145+0j)] + [(0.05546175587793897+0j)] * 32 + [(0.054696778353937145+0j), (0.04894482777418412+0j), (0.03919195427811065+0j), (0.028082262362842645+0j), (0.018005795889799343+0j), (0.01033088698487238+0j), (0.005304054232824478+0j), (0.002436819486646631+0j), (0.0010018064407078446+0j), (0.0003685439935695536+0j)],
        },
        "q12_1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0003685439935695536+0j), (-0.0010018064407078446+0j), (-0.002436819486646631+0j), (-0.005304054232824478+0j), (-0.01033088698487238+0j), (-0.018005795889799343+0j), (-0.028082262362842645+0j), (-0.03919195427811065+0j), (-0.04894482777418412+0j), (-0.054696778353937145+0j)] + [(-0.05546175587793897+0j)] * 32 + [(-0.054696778353937145+0j), (-0.04894482777418412+0j), (-0.03919195427811065+0j), (-0.028082262362842645+0j), (-0.018005795889799343+0j), (-0.01033088698487238+0j), (-0.005304054232824478+0j), (-0.002436819486646631+0j), (-0.0010018064407078446+0j), (-0.0003685439935695536+0j)],
        },
        "q12_2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0011846004105641446+0j), (0.003220077770021639+0j), (0.007832599132585027+0j), (0.01704866971511929+0j), (0.03320627435883577+0j), (0.05787551439110632+0j), (0.09026401218044879+0j), (0.12597357693715647+0j), (0.15732195908206426+0j), (0.17581028920603403+0j)] + [(0.17826913456728366+0j)] * 32 + [(0.17581028920603403+0j), (0.15732195908206426+0j), (0.12597357693715647+0j), (0.09026401218044879+0j), (0.05787551439110632+0j), (0.03320627435883577+0j), (0.01704866971511929+0j), (0.007832599132585027+0j), (0.003220077770021639+0j), (0.0011846004105641446+0j)],
        },
        "q12_2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0003368503543574758+0j), (0.0009156541971599167+0j), (0.0022272605764966998+0j), (0.004847922036534303+0j), (0.009442462778936971+0j), (0.016457353346670735+0j), (0.025667274987885267+0j), (0.03582156789119409+0j), (0.04473572454678471+0j), (0.049993025235015386+0j)] + [(0.05069221706701275+0j)] * 32 + [(0.049993025235015386+0j), (0.04473572454678471+0j), (0.03582156789119409+0j), (0.025667274987885267+0j), (0.016457353346670735+0j), (0.009442462778936971+0j), (0.004847922036534303+0j), (0.0022272605764966998+0j), (0.0009156541971599167+0j), (0.0003368503543574758+0j)],
        },
        "q12_2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0003368503543574758+0j), (-0.0009156541971599167+0j), (-0.0022272605764966998+0j), (-0.004847922036534303+0j), (-0.009442462778936971+0j), (-0.016457353346670735+0j), (-0.025667274987885267+0j), (-0.03582156789119409+0j), (-0.04473572454678471+0j), (-0.049993025235015386+0j)] + [(-0.05069221706701275+0j)] * 32 + [(-0.049993025235015386+0j), (-0.04473572454678471+0j), (-0.03582156789119409+0j), (-0.025667274987885267+0j), (-0.016457353346670735+0j), (-0.009442462778936971+0j), (-0.004847922036534303+0j), (-0.0022272605764966998+0j), (-0.0009156541971599167+0j), (-0.0003368503543574758+0j)],
        },
        "q12_2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0011846004105641446+0j), (0.003220077770021639+0j), (0.007832599132585027+0j), (0.01704866971511929+0j), (0.03320627435883577+0j), (0.05787551439110632+0j), (0.09026401218044879+0j), (0.12597357693715647+0j), (0.15732195908206426+0j), (0.17581028920603403+0j)] + [(0.17826913456728366+0j)] * 32 + [(0.17581028920603403+0j), (0.15732195908206426+0j), (0.12597357693715647+0j), (0.09026401218044879+0j), (0.05787551439110632+0j), (0.03320627435883577+0j), (0.01704866971511929+0j), (0.007832599132585027+0j), (0.003220077770021639+0j), (0.0011846004105641446+0j)],
        },
        "q12_2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0003368503543574758+0j), (0.0009156541971599167+0j), (0.0022272605764966998+0j), (0.004847922036534303+0j), (0.009442462778936971+0j), (0.016457353346670735+0j), (0.025667274987885267+0j), (0.03582156789119409+0j), (0.04473572454678471+0j), (0.049993025235015386+0j)] + [(0.05069221706701275+0j)] * 32 + [(0.049993025235015386+0j), (0.04473572454678471+0j), (0.03582156789119409+0j), (0.025667274987885267+0j), (0.016457353346670735+0j), (0.009442462778936971+0j), (0.004847922036534303+0j), (0.0022272605764966998+0j), (0.0009156541971599167+0j), (0.0003368503543574758+0j)],
        },
        "q12_2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0003368503543574758+0j), (-0.0009156541971599167+0j), (-0.0022272605764966998+0j), (-0.004847922036534303+0j), (-0.009442462778936971+0j), (-0.016457353346670735+0j), (-0.025667274987885267+0j), (-0.03582156789119409+0j), (-0.04473572454678471+0j), (-0.049993025235015386+0j)] + [(-0.05069221706701275+0j)] * 32 + [(-0.049993025235015386+0j), (-0.04473572454678471+0j), (-0.03582156789119409+0j), (-0.025667274987885267+0j), (-0.016457353346670735+0j), (-0.009442462778936971+0j), (-0.004847922036534303+0j), (-0.0022272605764966998+0j), (-0.0009156541971599167+0j), (-0.0003368503543574758+0j)],
        },
        "q12_3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006342512019745167+0j), (0.0017240735170056364+0j), (0.004193680307826982+0j), (0.009128090082065216+0j), (0.017779091782651992+0j), (0.030987339055514325+0j), (0.04832858211928844+0j), (0.06744796969247237+0j), (0.08423232066690386+0j), (0.09413122454964444+0j)] + [(0.09544772386193097+0j)] * 32 + [(0.09413122454964444+0j), (0.08423232066690386+0j), (0.06744796969247237+0j), (0.04832858211928844+0j), (0.030987339055514325+0j), (0.017779091782651992+0j), (0.009128090082065216+0j), (0.004193680307826982+0j), (0.0017240735170056364+0j), (0.0006342512019745167+0j)],
        },
        "q12_3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00032851703240092234+0j), (0.0008930018795147186+0j), (0.002172160502457921+0j), (0.004727989566141715+0j), (0.009208866223725546+0j), (0.016050215808542965+0j), (0.02503229371666342+0j), (0.03493538013937992+0j), (0.043629009975208445+0j), (0.04875625059762442+0j)] + [(0.04943814516224458+0j)] * 32 + [(0.04875625059762442+0j), (0.043629009975208445+0j), (0.03493538013937992+0j), (0.02503229371666342+0j), (0.016050215808542965+0j), (0.009208866223725546+0j), (0.004727989566141715+0j), (0.002172160502457921+0j), (0.0008930018795147186+0j), (0.00032851703240092234+0j)],
        },
        "q12_3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00032851703240092234+0j), (-0.0008930018795147186+0j), (-0.002172160502457921+0j), (-0.004727989566141715+0j), (-0.009208866223725546+0j), (-0.016050215808542965+0j), (-0.02503229371666342+0j), (-0.03493538013937992+0j), (-0.043629009975208445+0j), (-0.04875625059762442+0j)] + [(-0.04943814516224458+0j)] * 32 + [(-0.04875625059762442+0j), (-0.043629009975208445+0j), (-0.03493538013937992+0j), (-0.02503229371666342+0j), (-0.016050215808542965+0j), (-0.009208866223725546+0j), (-0.004727989566141715+0j), (-0.002172160502457921+0j), (-0.0008930018795147186+0j), (-0.00032851703240092234+0j)],
        },
        "q12_3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0006342512019745167+0j), (0.0017240735170056364+0j), (0.004193680307826982+0j), (0.009128090082065216+0j), (0.017779091782651992+0j), (0.030987339055514325+0j), (0.04832858211928844+0j), (0.06744796969247237+0j), (0.08423232066690386+0j), (0.09413122454964444+0j)] + [(0.09544772386193097+0j)] * 32 + [(0.09413122454964444+0j), (0.08423232066690386+0j), (0.06744796969247237+0j), (0.04832858211928844+0j), (0.030987339055514325+0j), (0.017779091782651992+0j), (0.009128090082065216+0j), (0.004193680307826982+0j), (0.0017240735170056364+0j), (0.0006342512019745167+0j)],
        },
        "q12_3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00032851703240092234+0j), (0.0008930018795147186+0j), (0.002172160502457921+0j), (0.004727989566141715+0j), (0.009208866223725546+0j), (0.016050215808542965+0j), (0.02503229371666342+0j), (0.03493538013937992+0j), (0.043629009975208445+0j), (0.04875625059762442+0j)] + [(0.04943814516224458+0j)] * 32 + [(0.04875625059762442+0j), (0.043629009975208445+0j), (0.03493538013937992+0j), (0.02503229371666342+0j), (0.016050215808542965+0j), (0.009208866223725546+0j), (0.004727989566141715+0j), (0.002172160502457921+0j), (0.0008930018795147186+0j), (0.00032851703240092234+0j)],
        },
        "q12_3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00032851703240092234+0j), (-0.0008930018795147186+0j), (-0.002172160502457921+0j), (-0.004727989566141715+0j), (-0.009208866223725546+0j), (-0.016050215808542965+0j), (-0.02503229371666342+0j), (-0.03493538013937992+0j), (-0.043629009975208445+0j), (-0.04875625059762442+0j)] + [(-0.04943814516224458+0j)] * 32 + [(-0.04875625059762442+0j), (-0.043629009975208445+0j), (-0.03493538013937992+0j), (-0.02503229371666342+0j), (-0.016050215808542965+0j), (-0.009208866223725546+0j), (-0.004727989566141715+0j), (-0.002172160502457921+0j), (-0.0008930018795147186+0j), (-0.00032851703240092234+0j)],
        },
        "q12_4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00044079793703683873+0j), (0.001198213022269473+0j), (0.0029145638550266725+0j), (0.00634392692474935+0j), (0.012356282425297615+0j), (0.02153587582870766+0j), (0.033587857983994364+0j), (0.04687563193448955+0j), (0.058540579925126415+0j), (0.06542021436153592+0j)] + [(0.0663351675837919+0j)] * 32 + [(0.06542021436153592+0j), (0.058540579925126415+0j), (0.04687563193448955+0j), (0.033587857983994364+0j), (0.02153587582870766+0j), (0.012356282425297615+0j), (0.00634392692474935+0j), (0.0029145638550266725+0j), (0.001198213022269473+0j), (0.00044079793703683873+0j)],
        },
        "q12_4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00022595032861955896+0j), (0.0006141966724208969+0j), (0.0014939876199350922+0j), (0.0032518581711642393+0j), (0.006333754856658392+0j), (0.011039158334808279+0j), (0.01721693073276873+0j), (0.024028162452498593+0j), (0.03000754350299156+0j), (0.03353400207069409+0j)] + [(0.03400300150075038+0j)] * 32 + [(0.03353400207069409+0j), (0.03000754350299156+0j), (0.024028162452498593+0j), (0.01721693073276873+0j), (0.011039158334808279+0j), (0.006333754856658392+0j), (0.0032518581711642393+0j), (0.0014939876199350922+0j), (0.0006141966724208969+0j), (0.00022595032861955896+0j)],
        },
        "q12_4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00022595032861955896+0j), (-0.0006141966724208969+0j), (-0.0014939876199350922+0j), (-0.0032518581711642393+0j), (-0.006333754856658392+0j), (-0.011039158334808279+0j), (-0.01721693073276873+0j), (-0.024028162452498593+0j), (-0.03000754350299156+0j), (-0.03353400207069409+0j)] + [(-0.03400300150075038+0j)] * 32 + [(-0.03353400207069409+0j), (-0.03000754350299156+0j), (-0.024028162452498593+0j), (-0.01721693073276873+0j), (-0.011039158334808279+0j), (-0.006333754856658392+0j), (-0.0032518581711642393+0j), (-0.0014939876199350922+0j), (-0.0006141966724208969+0j), (-0.00022595032861955896+0j)],
        },
        "q12_4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00044079793703683873+0j), (0.001198213022269473+0j), (0.0029145638550266725+0j), (0.00634392692474935+0j), (0.012356282425297615+0j), (0.02153587582870766+0j), (0.033587857983994364+0j), (0.04687563193448955+0j), (0.058540579925126415+0j), (0.06542021436153592+0j)] + [(0.0663351675837919+0j)] * 32 + [(0.06542021436153592+0j), (0.058540579925126415+0j), (0.04687563193448955+0j), (0.033587857983994364+0j), (0.02153587582870766+0j), (0.012356282425297615+0j), (0.00634392692474935+0j), (0.0029145638550266725+0j), (0.001198213022269473+0j), (0.00044079793703683873+0j)],
        },
        "q12_4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00022595032861955896+0j), (0.0006141966724208969+0j), (0.0014939876199350922+0j), (0.0032518581711642393+0j), (0.006333754856658392+0j), (0.011039158334808279+0j), (0.01721693073276873+0j), (0.024028162452498593+0j), (0.03000754350299156+0j), (0.03353400207069409+0j)] + [(0.03400300150075038+0j)] * 32 + [(0.03353400207069409+0j), (0.03000754350299156+0j), (0.024028162452498593+0j), (0.01721693073276873+0j), (0.011039158334808279+0j), (0.006333754856658392+0j), (0.0032518581711642393+0j), (0.0014939876199350922+0j), (0.0006141966724208969+0j), (0.00022595032861955896+0j)],
        },
        "q12_4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00022595032861955896+0j), (-0.0006141966724208969+0j), (-0.0014939876199350922+0j), (-0.0032518581711642393+0j), (-0.006333754856658392+0j), (-0.011039158334808279+0j), (-0.01721693073276873+0j), (-0.024028162452498593+0j), (-0.03000754350299156+0j), (-0.03353400207069409+0j)] + [(-0.03400300150075038+0j)] * 32 + [(-0.03353400207069409+0j), (-0.03000754350299156+0j), (-0.024028162452498593+0j), (-0.01721693073276873+0j), (-0.011039158334808279+0j), (-0.006333754856658392+0j), (-0.0032518581711642393+0j), (-0.0014939876199350922+0j), (-0.0006141966724208969+0j), (-0.00022595032861955896+0j)],
        },
        "q12_5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005376176462019842+0j), (0.0014613962783297776+0j), (0.003554737506209946+0j), (0.0077373480554109395+0j), (0.015070296195012088+0j), (0.02626615485035813+0j), (0.04096531229639685+0j), (0.05717169883838341+0j), (0.07139881143321992+0j), (0.07978953326212786+0j)] + [(0.08090545272636318+0j)] * 32 + [(0.07978953326212786+0j), (0.07139881143321992+0j), (0.05717169883838341+0j), (0.04096531229639685+0j), (0.02626615485035813+0j), (0.015070296195012088+0j), (0.0077373480554109395+0j), (0.003554737506209946+0j), (0.0014613962783297776+0j), (0.0005376176462019842+0j)],
        },
        "q12_5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0002308102618338501+0j), (0.0006274073405648289+0j), (0.0015261215853965336+0j), (0.003321801922212349+0j), (0.006469986681533849+0j), (0.01127659800828397+0j), (0.0175872472267855+0j), (0.024544980752762718+0j), (0.03065297145275578+0j), (0.034255280112054566+0j)] + [(0.0347343671835918+0j)] * 32 + [(0.034255280112054566+0j), (0.03065297145275578+0j), (0.024544980752762718+0j), (0.0175872472267855+0j), (0.01127659800828397+0j), (0.006469986681533849+0j), (0.003321801922212349+0j), (0.0015261215853965336+0j), (0.0006274073405648289+0j), (0.0002308102618338501+0j)],
        },
        "q12_5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0002623693252915482+0j), (0.0007131937692850755+0j), (0.0017347906782480568+0j), (0.003775997315537051+0j), (0.007354638510402588+0j), (0.012818465641476843+0j), (0.019991980217712455+0j), (0.02790105599391481+0j), (0.03484420222195312+0j), (0.03893906041813023+0j)] + [(0.03948365384615385+0j)] * 32 + [(0.03893906041813023+0j), (0.03484420222195312+0j), (0.02790105599391481+0j), (0.019991980217712455+0j), (0.012818465641476843+0j), (0.007354638510402588+0j), (0.003775997315537051+0j), (0.0017347906782480568+0j), (0.0007131937692850755+0j), (0.0002623693252915482+0j)],
        },
        "q12_5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002623693252915482+0j), (-0.0007131937692850755+0j), (-0.0017347906782480568+0j), (-0.003775997315537051+0j), (-0.007354638510402588+0j), (-0.012818465641476843+0j), (-0.019991980217712455+0j), (-0.02790105599391481+0j), (-0.03484420222195312+0j), (-0.03893906041813023+0j)] + [(-0.03948365384615385+0j)] * 32 + [(-0.03893906041813023+0j), (-0.03484420222195312+0j), (-0.02790105599391481+0j), (-0.019991980217712455+0j), (-0.012818465641476843+0j), (-0.007354638510402588+0j), (-0.003775997315537051+0j), (-0.0017347906782480568+0j), (-0.0007131937692850755+0j), (-0.0002623693252915482+0j)],
        },
        "q12_5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005376176462019842+0j), (0.0014613962783297776+0j), (0.003554737506209946+0j), (0.0077373480554109395+0j), (0.015070296195012088+0j), (0.02626615485035813+0j), (0.04096531229639685+0j), (0.05717169883838341+0j), (0.07139881143321992+0j), (0.07978953326212786+0j)] + [(0.08090545272636318+0j)] * 32 + [(0.07978953326212786+0j), (0.07139881143321992+0j), (0.05717169883838341+0j), (0.04096531229639685+0j), (0.02626615485035813+0j), (0.015070296195012088+0j), (0.0077373480554109395+0j), (0.003554737506209946+0j), (0.0014613962783297776+0j), (0.0005376176462019842+0j)],
        },
        "q12_5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0002623693252915482+0j), (0.0007131937692850755+0j), (0.0017347906782480568+0j), (0.003775997315537051+0j), (0.007354638510402588+0j), (0.012818465641476843+0j), (0.019991980217712455+0j), (0.02790105599391481+0j), (0.03484420222195312+0j), (0.03893906041813023+0j)] + [(0.03948365384615385+0j)] * 32 + [(0.03893906041813023+0j), (0.03484420222195312+0j), (0.02790105599391481+0j), (0.019991980217712455+0j), (0.012818465641476843+0j), (0.007354638510402588+0j), (0.003775997315537051+0j), (0.0017347906782480568+0j), (0.0007131937692850755+0j), (0.0002623693252915482+0j)],
        },
        "q12_5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002623693252915482+0j), (-0.0007131937692850755+0j), (-0.0017347906782480568+0j), (-0.003775997315537051+0j), (-0.007354638510402588+0j), (-0.012818465641476843+0j), (-0.019991980217712455+0j), (-0.02790105599391481+0j), (-0.03484420222195312+0j), (-0.03893906041813023+0j)] + [(-0.03948365384615385+0j)] * 32 + [(-0.03893906041813023+0j), (-0.03484420222195312+0j), (-0.02790105599391481+0j), (-0.019991980217712455+0j), (-0.012818465641476843+0j), (-0.007354638510402588+0j), (-0.003775997315537051+0j), (-0.0017347906782480568+0j), (-0.0007131937692850755+0j), (-0.0002623693252915482+0j)],
        },
        "q12_6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 84 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005184504950982889+0j), (0.0014092945597812742+0j), (0.003428003959800458+0j), (0.007461496024943498+0j), (0.0145330098049766+0j), (0.025329713566321993+0j), (0.03950481646568502+0j), (0.05513341271025556+0j), (0.06885330010740563+0j), (0.076944875815832+0j)] + [(0.07802101050525263+0j)] * 84 + [(0.076944875815832+0j), (0.06885330010740563+0j), (0.05513341271025556+0j), (0.03950481646568502+0j), (0.025329713566321993+0j), (0.0145330098049766+0j), (0.007461496024943498+0j), (0.003428003959800458+0j), (0.0014092945597812742+0j), (0.0005184504950982889+0j)],
        },
        "q12_6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 84 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0002329443775134499+0j), (0.0006332084684365146+0j), (0.001540232396495197+0j), (0.0033525159360104934+0j), (0.006529809411745918+0j), (0.011380863583093407+0j), (0.017749862267249776+0j), (0.024771928323740536+0j), (0.030936394670094108+0j), (0.03457201096195432+0j)] + [(0.03505552776388195+0j)] * 84 + [(0.03457201096195432+0j), (0.030936394670094108+0j), (0.024771928323740536+0j), (0.017749862267249776+0j), (0.011380863583093407+0j), (0.006529809411745918+0j), (0.0033525159360104934+0j), (0.001540232396495197+0j), (0.0006332084684365146+0j), (0.0002329443775134499+0j)],
        },
        "q12_6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002329443775134499+0j), (-0.0006332084684365146+0j), (-0.001540232396495197+0j), (-0.0033525159360104934+0j), (-0.006529809411745918+0j), (-0.011380863583093407+0j), (-0.017749862267249776+0j), (-0.024771928323740536+0j), (-0.030936394670094108+0j), (-0.03457201096195432+0j)] + [(-0.03505552776388195+0j)] * 84 + [(-0.03457201096195432+0j), (-0.030936394670094108+0j), (-0.024771928323740536+0j), (-0.017749862267249776+0j), (-0.011380863583093407+0j), (-0.006529809411745918+0j), (-0.0033525159360104934+0j), (-0.001540232396495197+0j), (-0.0006332084684365146+0j), (-0.0002329443775134499+0j)],
        },
        "q12_6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005184504950982889+0j), (0.0014092945597812742+0j), (0.003428003959800458+0j), (0.007461496024943498+0j), (0.0145330098049766+0j), (0.025329713566321993+0j), (0.03950481646568502+0j), (0.05513341271025556+0j), (0.06885330010740563+0j), (0.076944875815832+0j)] + [(0.07802101050525263+0j)] * 84 + [(0.076944875815832+0j), (0.06885330010740563+0j), (0.05513341271025556+0j), (0.03950481646568502+0j), (0.025329713566321993+0j), (0.0145330098049766+0j), (0.007461496024943498+0j), (0.003428003959800458+0j), (0.0014092945597812742+0j), (0.0005184504950982889+0j)],
        },
        "q12_6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0002329443775134499+0j), (0.0006332084684365146+0j), (0.001540232396495197+0j), (0.0033525159360104934+0j), (0.006529809411745918+0j), (0.011380863583093407+0j), (0.017749862267249776+0j), (0.024771928323740536+0j), (0.030936394670094108+0j), (0.03457201096195432+0j)] + [(0.03505552776388195+0j)] * 84 + [(0.03457201096195432+0j), (0.030936394670094108+0j), (0.024771928323740536+0j), (0.017749862267249776+0j), (0.011380863583093407+0j), (0.006529809411745918+0j), (0.0033525159360104934+0j), (0.001540232396495197+0j), (0.0006332084684365146+0j), (0.0002329443775134499+0j)],
        },
        "q12_6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0002329443775134499+0j), (-0.0006332084684365146+0j), (-0.001540232396495197+0j), (-0.0033525159360104934+0j), (-0.006529809411745918+0j), (-0.011380863583093407+0j), (-0.017749862267249776+0j), (-0.024771928323740536+0j), (-0.030936394670094108+0j), (-0.03457201096195432+0j)] + [(-0.03505552776388195+0j)] * 84 + [(-0.03457201096195432+0j), (-0.030936394670094108+0j), (-0.024771928323740536+0j), (-0.017749862267249776+0j), (-0.011380863583093407+0j), (-0.006529809411745918+0j), (-0.0033525159360104934+0j), (-0.001540232396495197+0j), (-0.0006332084684365146+0j), (-0.0002329443775134499+0j)],
        },
        "q12_7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 84 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0004627241473524776+0j), (0.0012578146413374455+0j), (0.0030595403503643386+0j), (0.006659487103896635+0j), (0.012970909728224093+0j), (0.022607115285784032+0j), (0.035258588212814204+0j), (0.049207323800797446+0j), (0.061452510675225454+0j), (0.06867435250162739+0j)] + [(0.06963481740870435+0j)] * 84 + [(0.06867435250162739+0j), (0.061452510675225454+0j), (0.049207323800797446+0j), (0.035258588212814204+0j), (0.022607115285784032+0j), (0.012970909728224093+0j), (0.006659487103896635+0j), (0.0030595403503643386+0j), (0.0012578146413374455+0j), (0.0004627241473524776+0j)],
        },
        "q12_7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 84 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0005964190784955906+0j), (0.0016212351432208527+0j), (0.003943533629755371+0j), (0.00858361333525516+0j), (0.016718595888327338+0j), (0.029138991218282048+0j), (0.04544585540059031+0j), (0.0634248004657296+0j), (0.0792079903282838+0j), (0.08851643958857824+0j)] + [(0.08975441171102691+0j)] * 84 + [(0.08851643958857824+0j), (0.0792079903282838+0j), (0.0634248004657296+0j), (0.04544585540059031+0j), (0.029138991218282048+0j), (0.016718595888327338+0j), (0.00858361333525516+0j), (0.003943533629755371+0j), (0.0016212351432208527+0j), (0.0005964190784955906+0j)],
        },
        "q12_7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005964190784955906+0j), (-0.0016212351432208527+0j), (-0.003943533629755371+0j), (-0.00858361333525516+0j), (-0.016718595888327338+0j), (-0.029138991218282048+0j), (-0.04544585540059031+0j), (-0.0634248004657296+0j), (-0.0792079903282838+0j), (-0.08851643958857824+0j)] + [(-0.08975441171102691+0j)] * 84 + [(-0.08851643958857824+0j), (-0.0792079903282838+0j), (-0.0634248004657296+0j), (-0.04544585540059031+0j), (-0.029138991218282048+0j), (-0.016718595888327338+0j), (-0.00858361333525516+0j), (-0.003943533629755371+0j), (-0.0016212351432208527+0j), (-0.0005964190784955906+0j)],
        },
        "q12_7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0004627241473524776+0j), (0.0012578146413374455+0j), (0.0030595403503643386+0j), (0.006659487103896635+0j), (0.012970909728224093+0j), (0.022607115285784032+0j), (0.035258588212814204+0j), (0.049207323800797446+0j), (0.061452510675225454+0j), (0.06867435250162739+0j)] + [(0.06963481740870435+0j)] * 84 + [(0.06867435250162739+0j), (0.061452510675225454+0j), (0.049207323800797446+0j), (0.035258588212814204+0j), (0.022607115285784032+0j), (0.012970909728224093+0j), (0.006659487103896635+0j), (0.0030595403503643386+0j), (0.0012578146413374455+0j), (0.0004627241473524776+0j)],
        },
        "q12_7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0005964190784955906+0j), (0.0016212351432208527+0j), (0.003943533629755371+0j), (0.00858361333525516+0j), (0.016718595888327338+0j), (0.029138991218282048+0j), (0.04544585540059031+0j), (0.0634248004657296+0j), (0.0792079903282838+0j), (0.08851643958857824+0j)] + [(0.08975441171102691+0j)] * 84 + [(0.08851643958857824+0j), (0.0792079903282838+0j), (0.0634248004657296+0j), (0.04544585540059031+0j), (0.029138991218282048+0j), (0.016718595888327338+0j), (0.00858361333525516+0j), (0.003943533629755371+0j), (0.0016212351432208527+0j), (0.0005964190784955906+0j)],
        },
        "q12_7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.0005964190784955906+0j), (-0.0016212351432208527+0j), (-0.003943533629755371+0j), (-0.00858361333525516+0j), (-0.016718595888327338+0j), (-0.029138991218282048+0j), (-0.04544585540059031+0j), (-0.0634248004657296+0j), (-0.0792079903282838+0j), (-0.08851643958857824+0j)] + [(-0.08975441171102691+0j)] * 84 + [(-0.08851643958857824+0j), (-0.0792079903282838+0j), (-0.0634248004657296+0j), (-0.04544585540059031+0j), (-0.029138991218282048+0j), (-0.016718595888327338+0j), (-0.00858361333525516+0j), (-0.003943533629755371+0j), (-0.0016212351432208527+0j), (-0.0005964190784955906+0j)],
        },
        "q12_8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00265800451309656+0j), (0.0072252053679125105+0j), (0.01757477344936297+0j), (0.038253777933015445+0j), (0.07450818547908036+0j), (0.1298609869433399+0j), (0.20253424665924025+0j), (0.2826593111430865+0j), (0.3529987610338382+0j), (0.3944828466975665+0j)] + [(0.4+0j)] * 32 + [(0.3944828466975665+0j), (0.3529987610338382+0j), (0.2826593111430865+0j), (0.20253424665924025+0j), (0.1298609869433399+0j), (0.07450818547908036+0j), (0.038253777933015445+0j), (0.01757477344936297+0j), (0.0072252053679125105+0j), (0.00265800451309656+0j)],
        },
        "q12_8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 32 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q12_8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [(0.0006199838740978153+0j), (0.001685290898897732+0j), (0.004099344480357415+0j), (0.008922755896361738+0j), (0.017379155399365083+0j), (0.03029028633420265+0j), (0.047241442316060006+0j), (0.06593074387528111+0j), (0.08233753492108442+0j), (0.09201376534751093+0j)] + [(0.09330065032516259+0j)] * 32 + [(0.09201376534751093+0j), (0.08233753492108442+0j), (0.06593074387528111+0j), (0.047241442316060006+0j), (0.03029028633420265+0j), (0.017379155399365083+0j), (0.008922755896361738+0j), (0.004099344480357415+0j), (0.001685290898897732+0j), (0.0006199838740978153+0j)],
        },
        "q12_8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 32 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q12_8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 32 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
        "q12_8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.0009761601314482508+0j), (0.002653478346981973+0j), (0.006454388273598899+0j), (0.014048814707233721+0j), (0.0273633546417487+0j), (0.04769183703790241+0j), (0.07438130968834596+0j), (0.10380747999523195+0j), (0.12963985398596017+0j), (0.1448750088982214+0j)] + [(0.1469012+0j)] * 32 + [(0.1448750088982214+0j), (0.12963985398596017+0j), (0.10380747999523195+0j), (0.07438130968834596+0j), (0.04769183703790241+0j), (0.0273633546417487+0j), (0.014048814707233721+0j), (0.006454388273598899+0j), (0.002653478346981973+0j), (0.0009761601314482508+0j)],
        },
        "q12_8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [(0.00044312470379322073+0j), (0.0012045378300624087+0j), (0.0029299484784956835+0j), (0.006377413556680184+0j), (0.012421505478229568+0j), (0.021649553674581108+0j), (0.03376515262357592+0j), (0.04712306653639073+0j), (0.05884958834786258+0j), (0.06576553716634542+0j)] + [(0.06668532+0j)] * 32 + [(0.06576553716634542+0j), (0.05884958834786258+0j), (0.04712306653639073+0j), (0.03376515262357592+0j), (0.021649553674581108+0j), (0.012421505478229568+0j), (0.006377413556680184+0j), (0.0029299484784956835+0j), (0.0012045378300624087+0j), (0.00044312470379322073+0j)],
        },
        "q12_8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [(-0.00044312470379322073+0j), (-0.0012045378300624087+0j), (-0.0029299484784956835+0j), (-0.006377413556680184+0j), (-0.012421505478229568+0j), (-0.021649553674581108+0j), (-0.03376515262357592+0j), (-0.04712306653639073+0j), (-0.05884958834786258+0j), (-0.06576553716634542+0j)] + [(-0.06668532+0j)] * 32 + [(-0.06576553716634542+0j), (-0.05884958834786258+0j), (-0.04712306653639073+0j), (-0.03376515262357592+0j), (-0.021649553674581108+0j), (-0.012421505478229568+0j), (-0.006377413556680184+0j), (-0.0029299484784956835+0j), (-0.0012045378300624087+0j), (-0.00044312470379322073+0j)],
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
    },
    "elements": {
        "q1": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q1",
            },
            "intermediate_frequency": 386784380.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q1_grft",
                "X180": "q1_X180",
                "X360": "q1_X360",
                "Y360": "q1_Y360",
                "X90": "q1_X90",
                "mX90": "q1_mX90",
                "Y180": "q1_Y180",
                "Y90": "q1_Y90",
                "mY90": "q1_mY90",
                "I": "zero",
                "d_X180": "q1_d_X180",
                "d_X90": "q1_d_X90",
                "d_mX90": "q1_d_mX90",
                "d_Y180": "q1_d_Y180",
                "d_Y90": "q1_d_Y90",
                "d_Y360": "q1_d_Y360",
                "d_X360": "q1_d_X360",
                "d_mY90": "q1_d_mY90",
            },
        },
        "rr1": {
            "mixInputs": {
                "I": ('con1', 5),
                "Q": ('con1', 6),
                "lo_frequency": 7388529000.0,
                "mixer": "mixer_rr1",
            },
            "intermediate_frequency": 22665000.0,
            "outputs": {
                "out1": ('con1', 1),
                "out2": ('con1', 2),
            },
            "time_of_flight": 340,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q1_ro_pulse",
            },
        },
        "q2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q2_grft",
                "X180": "q2_X180",
                "X360": "q2_X360",
                "Y360": "q2_Y360",
                "X90": "q2_X90",
                "mX90": "q2_mX90",
                "Y180": "q2_Y180",
                "Y90": "q2_Y90",
                "mY90": "q2_mY90",
                "I": "zero",
                "d_X180": "q2_d_X180",
                "d_X90": "q2_d_X90",
                "d_mX90": "q2_d_mX90",
                "d_Y180": "q2_d_Y180",
                "d_Y90": "q2_d_Y90",
                "d_Y360": "q2_d_Y360",
                "d_X360": "q2_d_X360",
                "d_mY90": "q2_d_mY90",
            },
        },
        "rr2": {
            "mixInputs": {
                "I": ('con1', 9),
                "Q": ('con1', 10),
                "lo_frequency": 7388529000.0,
                "mixer": "mixer_rr2",
            },
            "intermediate_frequency": 18800000.0,
            "outputs": {
                "out1": ('con1', 1),
                "out2": ('con1', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q2_ro_pulse",
            },
        },
        "q3": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q3",
            },
            "intermediate_frequency": 372844133.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q3_grft",
                "X180": "q3_X180",
                "X360": "q3_X360",
                "Y360": "q3_Y360",
                "X90": "q3_X90",
                "mX90": "q3_mX90",
                "Y180": "q3_Y180",
                "Y90": "q3_Y90",
                "mY90": "q3_mY90",
                "I": "zero",
                "d_X180": "q3_d_X180",
                "d_X90": "q3_d_X90",
                "d_mX90": "q3_d_mX90",
                "d_Y180": "q3_d_Y180",
                "d_Y90": "q3_d_Y90",
                "d_Y360": "q3_d_Y360",
                "d_X360": "q3_d_X360",
                "d_mY90": "q3_d_mY90",
            },
        },
        "rr3": {
            "mixInputs": {
                "I": ('con2', 8),
                "Q": ('con2', 7),
                "lo_frequency": 7337596000.0,
                "mixer": "mixer_rr3",
            },
            "intermediate_frequency": 43934000.0,
            "outputs": {
                "out1": ('con2', 1),
                "out2": ('con2', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q3_ro_pulse",
            },
        },
        "q4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q4_grft",
                "X180": "q4_X180",
                "X360": "q4_X360",
                "Y360": "q4_Y360",
                "X90": "q4_X90",
                "mX90": "q4_mX90",
                "Y180": "q4_Y180",
                "Y90": "q4_Y90",
                "mY90": "q4_mY90",
                "I": "zero",
                "d_X180": "q4_d_X180",
                "d_X90": "q4_d_X90",
                "d_mX90": "q4_d_mX90",
                "d_Y180": "q4_d_Y180",
                "d_Y90": "q4_d_Y90",
                "d_Y360": "q4_d_Y360",
                "d_X360": "q4_d_X360",
                "d_mY90": "q4_d_mY90",
            },
        },
        "rr4": {
            "mixInputs": {
                "I": ('con2', 9),
                "Q": ('con2', 10),
                "lo_frequency": 7337596000.0,
                "mixer": "mixer_rr4",
            },
            "intermediate_frequency": 20200000.0,
            "outputs": {
                "out1": ('con2', 1),
                "out2": ('con2', 2),
            },
            "time_of_flight": 340,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q4_ro_pulse",
            },
        },
        "q5": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q5",
            },
            "intermediate_frequency": 321812452.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q5_grft",
                "X180": "q5_X180",
                "X360": "q5_X360",
                "Y360": "q5_Y360",
                "X90": "q5_X90",
                "mX90": "q5_mX90",
                "Y180": "q5_Y180",
                "Y90": "q5_Y90",
                "mY90": "q5_mY90",
                "I": "zero",
                "d_X180": "q5_d_X180",
                "d_X90": "q5_d_X90",
                "d_mX90": "q5_d_mX90",
                "d_Y180": "q5_d_Y180",
                "d_Y90": "q5_d_Y90",
                "d_Y360": "q5_d_Y360",
                "d_X360": "q5_d_X360",
                "d_mY90": "q5_d_mY90",
            },
        },
        "rr5": {
            "mixInputs": {
                "I": ('con3', 7),
                "Q": ('con3', 8),
                "lo_frequency": 7381058000.0,
                "mixer": "mixer_rr5",
            },
            "intermediate_frequency": 18480000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q5_ro_pulse",
            },
        },
        "q6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q6_grft",
                "X180": "q6_X180",
                "X360": "q6_X360",
                "Y360": "q6_Y360",
                "X90": "q6_X90",
                "mX90": "q6_mX90",
                "Y180": "q6_Y180",
                "Y90": "q6_Y90",
                "mY90": "q6_mY90",
                "I": "zero",
                "d_X180": "q6_d_X180",
                "d_X90": "q6_d_X90",
                "d_mX90": "q6_d_mX90",
                "d_Y180": "q6_d_Y180",
                "d_Y90": "q6_d_Y90",
                "d_Y360": "q6_d_Y360",
                "d_X360": "q6_d_X360",
                "d_mY90": "q6_d_mY90",
            },
        },
        "rr6": {
            "mixInputs": {
                "I": ('con3', 9),
                "Q": ('con3', 10),
                "lo_frequency": 7381058000.0,
                "mixer": "mixer_rr6",
            },
            "intermediate_frequency": 20294000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q6_ro_pulse",
            },
        },
        "q7": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q7",
            },
            "intermediate_frequency": 125957720.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q7_grft",
                "X180": "q7_X180",
                "X360": "q7_X360",
                "Y360": "q7_Y360",
                "X90": "q7_X90",
                "mX90": "q7_mX90",
                "Y180": "q7_Y180",
                "Y90": "q7_Y90",
                "mY90": "q7_mY90",
                "I": "zero",
                "d_X180": "q7_d_X180",
                "d_X90": "q7_d_X90",
                "d_mX90": "q7_d_mX90",
                "d_Y180": "q7_d_Y180",
                "d_Y90": "q7_d_Y90",
                "d_Y360": "q7_d_Y360",
                "d_X360": "q7_d_X360",
                "d_mY90": "q7_d_mY90",
            },
        },
        "rr7": {
            "mixInputs": {
                "I": ('con3', 9),
                "Q": ('con3', 10),
                "lo_frequency": 7381058000.0,
                "mixer": "mixer_rr7",
            },
            "intermediate_frequency": 20544000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q7_ro_pulse",
            },
        },
        "q8": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4300000000.0,
                "mixer": "mixer_q8",
            },
            "intermediate_frequency": -140337100.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q8_grft",
                "X180": "q8_X180",
                "X360": "q8_X360",
                "Y360": "q8_Y360",
                "X90": "q8_X90",
                "mX90": "q8_mX90",
                "Y180": "q8_Y180",
                "Y90": "q8_Y90",
                "mY90": "q8_mY90",
                "I": "zero",
                "d_X180": "q8_d_X180",
                "d_X90": "q8_d_X90",
                "d_mX90": "q8_d_mX90",
                "d_Y180": "q8_d_Y180",
                "d_Y90": "q8_d_Y90",
                "d_Y360": "q8_d_Y360",
                "d_X360": "q8_d_X360",
                "d_mY90": "q8_d_mY90",
            },
        },
        "rr8": {
            "mixInputs": {
                "I": ('con3', 7),
                "Q": ('con3', 8),
                "lo_frequency": 7395117500.0,
                "mixer": "mixer_rr8",
            },
            "intermediate_frequency": 20000000.0,
            "outputs": {
                "out1": ('con3', 1),
                "out2": ('con3', 2),
            },
            "time_of_flight": 300,
            "smearing": 0,
            "operations": {
                "const": "const_pulse",
                "readout": "q8_ro_pulse",
            },
        },
        "cr_c1t2": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c1t2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c1t2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c1t2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c1t4": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c1t4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c1t4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c1t4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c1t6": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c1t6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c1t6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c1t6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c3t2": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c3t2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c3t2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c3t2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c3t4": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c3t4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c3t4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c3t4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c3t6": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c3t6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c3t6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c3t6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c5t2": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c5t2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c5t2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c5t2",
            },
            "intermediate_frequency": 281272650.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c5t4": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c5t4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c5t4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c5t4",
            },
            "intermediate_frequency": 260657535.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_c5t6": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_c5t6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "cr_ac_c5t6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_cr_ac_c5t6",
            },
            "intermediate_frequency": 148637621.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "q12_1": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_1",
            },
            "intermediate_frequency": 116063819.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_1_grft",
                "X180": "q12_1_X180",
                "X360": "q12_1_X360",
                "X90": "q12_1_X90",
                "mX90": "q12_1_mX90",
                "Y180": "q12_1_Y180",
                "Y90": "q12_1_Y90",
                "mY90": "q12_1_mY90",
                "I": "zero",
            },
        },
        "q12_2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_2",
            },
            "intermediate_frequency": 12572432.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_2_grft",
                "X180": "q12_2_X180",
                "X360": "q12_2_X360",
                "X90": "q12_2_X90",
                "mX90": "q12_2_mX90",
                "Y180": "q12_2_Y180",
                "Y90": "q12_2_Y90",
                "mY90": "q12_2_mY90",
                "I": "zero",
            },
        },
        "q12_3": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_3",
            },
            "intermediate_frequency": 102246113.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_3_grft",
                "X180": "q12_3_X180",
                "X360": "q12_3_X360",
                "X90": "q12_3_X90",
                "mX90": "q12_3_mX90",
                "Y180": "q12_3_Y180",
                "Y90": "q12_3_Y90",
                "mY90": "q12_3_mY90",
                "I": "zero",
            },
        },
        "q12_4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_4",
            },
            "intermediate_frequency": -21093907.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_4_grft",
                "X180": "q12_4_X180",
                "X360": "q12_4_X360",
                "X90": "q12_4_X90",
                "mX90": "q12_4_mX90",
                "Y180": "q12_4_Y180",
                "Y90": "q12_4_Y90",
                "mY90": "q12_4_mY90",
                "I": "zero",
            },
        },
        "q12_5": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_5",
            },
            "intermediate_frequency": 51366333.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_5_grft",
                "X180": "q12_5_X180",
                "X360": "q12_5_X360",
                "X90": "q12_5_X90",
                "mX90": "q12_5_mX90",
                "Y180": "q12_5_Y180",
                "Y90": "q12_5_Y90",
                "mY90": "q12_5_mY90",
                "I": "zero",
            },
        },
        "q12_6": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_6",
            },
            "intermediate_frequency": -146606483.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_6_grft",
                "X180": "q12_6_X180",
                "X360": "q12_6_X360",
                "X90": "q12_6_X90",
                "mX90": "q12_6_mX90",
                "Y180": "q12_6_Y180",
                "Y90": "q12_6_Y90",
                "mY90": "q12_6_mY90",
                "I": "zero",
            },
        },
        "q12_7": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 4700000000.0,
                "mixer": "mixer_q12_7",
            },
            "intermediate_frequency": -131548483.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_7_grft",
                "X180": "q12_7_X180",
                "X360": "q12_7_X360",
                "X90": "q12_7_X90",
                "mX90": "q12_7_mX90",
                "Y180": "q12_7_Y180",
                "Y90": "q12_7_Y90",
                "mY90": "q12_7_mY90",
                "I": "zero",
            },
        },
        "q12_8": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 4300000000.0,
                "mixer": "mixer_q12_8",
            },
            "intermediate_frequency": -204595000.0,
            "operations": {
                "const": "const_pulse",
                "grft": "q12_8_grft",
                "X180": "q12_8_X180",
                "X360": "q12_8_X360",
                "X90": "q12_8_X90",
                "mX90": "q12_8_mX90",
                "Y180": "q12_8_Y180",
                "Y90": "q12_8_Y90",
                "mY90": "q12_8_mY90",
                "I": "zero",
            },
        },
        "stark_1": {
            "mixInputs": {
                "I": ('con1', 1),
                "Q": ('con1', 2),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_1",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_2": {
            "mixInputs": {
                "I": ('con1', 3),
                "Q": ('con1', 4),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_2",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_3": {
            "mixInputs": {
                "I": ('con2', 2),
                "Q": ('con2', 1),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_3",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_4": {
            "mixInputs": {
                "I": ('con2', 4),
                "Q": ('con2', 3),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_4",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_5": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_5",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_6": {
            "mixInputs": {
                "I": ('con3', 5),
                "Q": ('con3', 6),
                "lo_frequency": 4770000000.0,
                "mixer": "mixer_stark_6",
            },
            "intermediate_frequency": 10000000.0,
            "sticky": {
                "analog": True,
                "duration": 320,
            },
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_7": {
            "mixInputs": {
                "I": ('con3', 3),
                "Q": ('con3', 4),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_7",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
        "stark_8": {
            "mixInputs": {
                "I": ('con3', 1),
                "Q": ('con3', 2),
                "lo_frequency": 40000000000.0,
                "mixer": "mixer_stark_8",
            },
            "intermediate_frequency": 40000000.0,
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
        },
    },
    "integration_weights": {
        "integW_cos_rr1": {
            "cosine": [(0.1975375761873655, 2400)],
            "sine": [(-0.9802953157054362, 2400)],
        },
        "integW_sin_rr1": {
            "cosine": [(0.9802953157054362, 2400)],
            "sine": [(0.1975375761873655, 2400)],
        },
        "integW_minus_sin_rr1": {
            "cosine": [(-0.9802953157054362, 2400)],
            "sine": [(-0.1975375761873655, 2400)],
        },
        "integW_cos_rr2": {
            "cosine": [(-0.9270072224269928, 2000)],
            "sine": [(-0.37504347690393414, 2000)],
        },
        "integW_sin_rr2": {
            "cosine": [(0.37504347690393414, 2000)],
            "sine": [(-0.9270072224269928, 2000)],
        },
        "integW_minus_sin_rr2": {
            "cosine": [(-0.37504347690393414, 2000)],
            "sine": [(0.9270072224269928, 2000)],
        },
        "integW_cos_rr3": {
            "cosine": [(-0.5876299213481043, 3600)],
            "sine": [(-0.8091298261320125, 3600)],
        },
        "integW_sin_rr3": {
            "cosine": [(0.8091298261320125, 3600)],
            "sine": [(-0.5876299213481043, 3600)],
        },
        "integW_minus_sin_rr3": {
            "cosine": [(-0.8091298261320125, 3600)],
            "sine": [(0.5876299213481043, 3600)],
        },
        "integW_cos_rr4": {
            "cosine": [(-0.05395681831328809, 3600)],
            "sine": [(-0.9985432698473846, 3600)],
        },
        "integW_sin_rr4": {
            "cosine": [(0.9985432698473846, 3600)],
            "sine": [(-0.05395681831328809, 3600)],
        },
        "integW_minus_sin_rr4": {
            "cosine": [(-0.9985432698473846, 3600)],
            "sine": [(0.05395681831328809, 3600)],
        },
        "integW_cos_rr5": {
            "cosine": [(-0.6153863701791713, 2800)],
            "sine": [(0.7882256119904402, 2800)],
        },
        "integW_sin_rr5": {
            "cosine": [(-0.7882256119904402, 2800)],
            "sine": [(-0.6153863701791713, 2800)],
        },
        "integW_minus_sin_rr5": {
            "cosine": [(0.7882256119904402, 2800)],
            "sine": [(0.6153863701791713, 2800)],
        },
        "integW_cos_rr6": {
            "cosine": [(0.9404899467342636, 2800)],
            "sine": [(-0.33982151210860984, 2800)],
        },
        "integW_sin_rr6": {
            "cosine": [(0.33982151210860984, 2800)],
            "sine": [(0.9404899467342636, 2800)],
        },
        "integW_minus_sin_rr6": {
            "cosine": [(-0.33982151210860984, 2800)],
            "sine": [(-0.9404899467342636, 2800)],
        },
        "integW_cos_rr7": {
            "cosine": [(0.8157137790818908, 3200)],
            "sine": [(0.5784557291754835, 3200)],
        },
        "integW_sin_rr7": {
            "cosine": [(-0.5784557291754835, 3200)],
            "sine": [(0.8157137790818908, 3200)],
        },
        "integW_minus_sin_rr7": {
            "cosine": [(0.5784557291754835, 3200)],
            "sine": [(-0.8157137790818908, 3200)],
        },
        "integW_cos_rr8": {
            "cosine": [(0.8416630519706616, 2000)],
            "sine": [(-0.5400030619796812, 2000)],
        },
        "integW_sin_rr8": {
            "cosine": [(0.5400030619796812, 2000)],
            "sine": [(0.8416630519706616, 2000)],
        },
        "integW_minus_sin_rr8": {
            "cosine": [(-0.5400030619796812, 2000)],
            "sine": [(-0.8416630519706616, 2000)],
        },
    },
    "mixers": {
        "mixer_q1": [{'intermediate_frequency': 386784380.0, 'lo_frequency': 4700000000.0, 'correction': [1.0236070453213617, 0.08572239907421268, 0.08783950028446405, 0.9989361431935753]}],
        "mixer_rr1": [{'intermediate_frequency': 22665000.0, 'lo_frequency': 7388529000.0, 'correction': [1.0362739520394184, 0.1694157628041169, 0.16806191786288155, 1.0446217935108408]}],
        "mixer_q2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': [1.0444961290328922, 0.06583338698039459, 0.07074813790071237, 0.9719367873490588]}],
        "mixer_rr2": [{'intermediate_frequency': 18800000.0, 'lo_frequency': 7388529000.0, 'correction': [1.1753568624073445, -0.1132445158954439, -0.14678881566699906, 0.9067633544347183]}],
        "mixer_q3": [{'intermediate_frequency': 372844133.0, 'lo_frequency': 4700000000.0, 'correction': [0.9716500277595905, -0.007498877298823346, -0.0070725332772443705, 1.030222700967818]}],
        "mixer_rr3": [{'intermediate_frequency': 43934000.0, 'lo_frequency': 7337596000.0, 'correction': [1.0656321623237386, -0.09872454699397955, -0.10843515817371514, 0.9702024164440017]}],
        "mixer_q4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': [1.0184918793231268, 0.12360451516601981, 0.12273714898578643, 1.0256894182774456]}],
        "mixer_rr4": [{'intermediate_frequency': 20200000.0, 'lo_frequency': 7337596000.0, 'correction': [1.0819225500106364, -0.10026910802347513, -0.11316000478976894, 0.9586727151663961]}],
        "mixer_q5": [{'intermediate_frequency': 321812452.0, 'lo_frequency': 4700000000.0, 'correction': [1.013073268410779, 0.06955989519263533, 0.07036171113358658, 1.0015286615091483]}],
        "mixer_rr5": [{'intermediate_frequency': 18480000.0, 'lo_frequency': 7381058000.0, 'correction': [0.9223695069723006, 0.06174919416041147, 0.051627611515804084, 1.1031998595604318]}],
        "mixer_q6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': [0.9958175654323856, 0.06271935271120836, 0.061482063944807264, 1.015857782172677]}],
        "mixer_rr6": [{'intermediate_frequency': 20294000.0, 'lo_frequency': 7381058000.0, 'correction': [0.991618959451214, 0.2878309591586392, 0.23602971047008225, 1.2092487663959264]}],
        "mixer_q7": [{'intermediate_frequency': 125957720.0, 'lo_frequency': 4700000000.0, 'correction': [0.9531282230165004, 0.04084422885368196, 0.03684101032608277, 1.0566970591527876]}],
        "mixer_rr7": [{'intermediate_frequency': 20544000.0, 'lo_frequency': 7381058000.0, 'correction': [1.433221002403429, 0.035912548247809734, 0.06669473246021809, 0.7717343859095386]}],
        "mixer_q8": [{'intermediate_frequency': -140337100.0, 'lo_frequency': 4300000000.0, 'correction': [0.9501664441395031, 0.05850250509417677, 0.0521698803260484, 1.0655021037269372]}],
        "mixer_rr8": [{'intermediate_frequency': 20000000.0, 'lo_frequency': 7395117500.0, 'correction': [1.4323943156170444, 0.032550787359555716, 0.060451462239174865, 0.7712892468707166]}],
        "mixer_cr_c1t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': [1.0028048404625798, 0.05428708474480452, 0.054116798179439, 1.0059603152459933]}],
        "mixer_cr_c1t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': [1.0035545076977206, 0.06183707871514085, 0.0615772911382139, 1.007788389848914]}],
        "mixer_cr_c1t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': [1.003347752519738, 0.054374655796432, 0.05426086251524492, 1.0054519253551555]}],
        "mixer_cr_c3t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': [0.9941242611207217, 0.03688402759555214, 0.036304000520180894, 1.0100073312912645]}],
        "mixer_cr_c3t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': [0.9924270368118341, 0.03533658614774343, 0.03467305253814176, 1.0114189814431196]}],
        "mixer_cr_c3t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': [1.000517709100806, 0.040676900393086524, 0.04051896463857211, 1.0044175500938168]}],
        "mixer_cr_c5t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': [0.9922471331276873, 0.05081242150795721, 0.04964643131256334, 1.0155509315689217]}],
        "mixer_cr_c5t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': [0.9839932556525414, 0.05317564250801031, 0.05105143646936771, 1.0249363624521883]}],
        "mixer_cr_c5t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': [0.9898378311367794, 0.051560209338117856, 0.050120314119192856, 1.0182746593093936]}],
        "mixer_q12_1": [{'intermediate_frequency': 116063819.0, 'lo_frequency': 4700000000.0, 'correction': [0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035]}],
        "mixer_q12_2": [{'intermediate_frequency': 12572432.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_3": [{'intermediate_frequency': 102246113.0, 'lo_frequency': 4700000000.0, 'correction': [1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166]}],
        "mixer_q12_4": [{'intermediate_frequency': -21093907.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_5": [{'intermediate_frequency': 51366333.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_6": [{'intermediate_frequency': -146606483.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_7": [{'intermediate_frequency': -131548483.0, 'lo_frequency': 4700000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_q12_8": [{'intermediate_frequency': -204595000.0, 'lo_frequency': 4300000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_1": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035]}],
        "mixer_stark_2": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_3": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166]}],
        "mixer_stark_4": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_5": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_6": [{'intermediate_frequency': 10000000.0, 'lo_frequency': 4770000000.0, 'correction': [1.0059032449415808, -0.017629670731559466, -0.017821119749575846, 0.9950970110365455]}],
        "mixer_stark_7": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
        "mixer_stark_8": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': [1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206]}],
    },
}

loaded_config = {
    "version": 1,
    "controllers": {
        "con1": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.03427316401433623,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "2": {
                    "offset": -0.004785346049418404,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "3": {
                    "offset": -0.027185835356852178,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "4": {
                    "offset": -0.007530590567993874,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "5": {
                    "offset": 0.0064196409297032665,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "6": {
                    "offset": 0.005306991551967946,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "7": {
                    "offset": -0.01004958944627166,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "8": {
                    "offset": 0.004911278856552271,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "9": {
                    "offset": 0.00821888106154563,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "10": {
                    "offset": 0.004321241386414653,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.20705431583788964,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
                "2": {
                    "offset": 0.24520065170098299,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
            },
            "digital_outputs": {},
            "digital_inputs": {},
        },
        "con2": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": -0.022996400577754886,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "2": {
                    "offset": -0.03074378496929838,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "3": {
                    "offset": -0.009657680853590173,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "4": {
                    "offset": -0.02716331607469863,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "5": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "6": {
                    "offset": 0.0,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "7": {
                    "offset": 0.009249489670579687,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "8": {
                    "offset": -0.0001508577334774491,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "9": {
                    "offset": -0.002423923022689978,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "10": {
                    "offset": -0.003703290379336752,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.20233268735851134,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
                "2": {
                    "offset": 0.193589471537298,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
            },
            "digital_outputs": {},
            "digital_inputs": {},
        },
        "con3": {
            "type": "opx1",
            "analog_outputs": {
                "1": {
                    "offset": 0.0035796135749611665,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "2": {
                    "offset": -0.00040874841867035756,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "3": {
                    "offset": -0.0015584675683137685,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "4": {
                    "offset": 0.002931144598262927,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "5": {
                    "offset": -0.0002090710667964095,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "6": {
                    "offset": -0.0043554795748769115,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "7": {
                    "offset": -0.008383220770184413,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "8": {
                    "offset": -0.0019318483019448605,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "9": {
                    "offset": -0.01119244502107044,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
                "10": {
                    "offset": -0.007203587297926902,
                    "delay": 0,
                    "shareable": False,
                    "filter": {
                        "feedforward": [],
                        "feedback": [],
                    },
                    "crosstalk": {},
                },
            },
            "analog_inputs": {
                "1": {
                    "offset": 0.2071748867439438,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
                "2": {
                    "offset": 0.23629523100002722,
                    "gain_db": 20,
                    "shareable": False,
                    "sampling_rate": 1000000000.0,
                },
            },
            "digital_outputs": {},
            "digital_inputs": {},
        },
    },
    "oscillators": {},
    "elements": {
        "q1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q1_grft",
                "X180": "q1_X180",
                "X360": "q1_X360",
                "Y360": "q1_Y360",
                "X90": "q1_X90",
                "mX90": "q1_mX90",
                "Y180": "q1_Y180",
                "Y90": "q1_Y90",
                "mY90": "q1_mY90",
                "I": "zero",
                "d_X180": "q1_d_X180",
                "d_X90": "q1_d_X90",
                "d_mX90": "q1_d_mX90",
                "d_Y180": "q1_d_Y180",
                "d_Y90": "q1_d_Y90",
                "d_Y360": "q1_d_Y360",
                "d_X360": "q1_d_X360",
                "d_mY90": "q1_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_q1",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 386784380.0,
        },
        "rr1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 1, 1),
                "out2": ('con1', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q1_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 5),
                "Q": ('con1', 1, 6),
                "mixer": "mixer_rr1",
                "lo_frequency": 7388529000.0,
            },
            "smearing": 0,
            "time_of_flight": 340,
            "intermediate_frequency": 22665000.0,
        },
        "q2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q2_grft",
                "X180": "q2_X180",
                "X360": "q2_X360",
                "Y360": "q2_Y360",
                "X90": "q2_X90",
                "mX90": "q2_mX90",
                "Y180": "q2_Y180",
                "Y90": "q2_Y90",
                "mY90": "q2_mY90",
                "I": "zero",
                "d_X180": "q2_d_X180",
                "d_X90": "q2_d_X90",
                "d_mX90": "q2_d_mX90",
                "d_Y180": "q2_d_Y180",
                "d_Y90": "q2_d_Y90",
                "d_Y360": "q2_d_Y360",
                "d_X360": "q2_d_X360",
                "d_mY90": "q2_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_q2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "rr2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con1', 1, 1),
                "out2": ('con1', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q2_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 9),
                "Q": ('con1', 1, 10),
                "mixer": "mixer_rr2",
                "lo_frequency": 7388529000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 18800000.0,
        },
        "q3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q3_grft",
                "X180": "q3_X180",
                "X360": "q3_X360",
                "Y360": "q3_Y360",
                "X90": "q3_X90",
                "mX90": "q3_mX90",
                "Y180": "q3_Y180",
                "Y90": "q3_Y90",
                "mY90": "q3_mY90",
                "I": "zero",
                "d_X180": "q3_d_X180",
                "d_X90": "q3_d_X90",
                "d_mX90": "q3_d_mX90",
                "d_Y180": "q3_d_Y180",
                "d_Y90": "q3_d_Y90",
                "d_Y360": "q3_d_Y360",
                "d_X360": "q3_d_X360",
                "d_mY90": "q3_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_q3",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 372844133.0,
        },
        "rr3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con2', 1, 1),
                "out2": ('con2', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q3_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 8),
                "Q": ('con2', 1, 7),
                "mixer": "mixer_rr3",
                "lo_frequency": 7337596000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 43934000.0,
        },
        "q4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q4_grft",
                "X180": "q4_X180",
                "X360": "q4_X360",
                "Y360": "q4_Y360",
                "X90": "q4_X90",
                "mX90": "q4_mX90",
                "Y180": "q4_Y180",
                "Y90": "q4_Y90",
                "mY90": "q4_mY90",
                "I": "zero",
                "d_X180": "q4_d_X180",
                "d_X90": "q4_d_X90",
                "d_mX90": "q4_d_mX90",
                "d_Y180": "q4_d_Y180",
                "d_Y90": "q4_d_Y90",
                "d_Y360": "q4_d_Y360",
                "d_X360": "q4_d_X360",
                "d_mY90": "q4_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_q4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "rr4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con2', 1, 1),
                "out2": ('con2', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q4_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 9),
                "Q": ('con2', 1, 10),
                "mixer": "mixer_rr4",
                "lo_frequency": 7337596000.0,
            },
            "smearing": 0,
            "time_of_flight": 340,
            "intermediate_frequency": 20200000.0,
        },
        "q5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q5_grft",
                "X180": "q5_X180",
                "X360": "q5_X360",
                "Y360": "q5_Y360",
                "X90": "q5_X90",
                "mX90": "q5_mX90",
                "Y180": "q5_Y180",
                "Y90": "q5_Y90",
                "mY90": "q5_mY90",
                "I": "zero",
                "d_X180": "q5_d_X180",
                "d_X90": "q5_d_X90",
                "d_mX90": "q5_d_mX90",
                "d_Y180": "q5_d_Y180",
                "d_Y90": "q5_d_Y90",
                "d_Y360": "q5_d_Y360",
                "d_X360": "q5_d_X360",
                "d_mY90": "q5_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q5",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 321812452.0,
        },
        "rr5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q5_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 7),
                "Q": ('con3', 1, 8),
                "mixer": "mixer_rr5",
                "lo_frequency": 7381058000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 18480000.0,
        },
        "q6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q6_grft",
                "X180": "q6_X180",
                "X360": "q6_X360",
                "Y360": "q6_Y360",
                "X90": "q6_X90",
                "mX90": "q6_mX90",
                "Y180": "q6_Y180",
                "Y90": "q6_Y90",
                "mY90": "q6_mY90",
                "I": "zero",
                "d_X180": "q6_d_X180",
                "d_X90": "q6_d_X90",
                "d_mX90": "q6_d_mX90",
                "d_Y180": "q6_d_Y180",
                "d_Y90": "q6_d_Y90",
                "d_Y360": "q6_d_Y360",
                "d_X360": "q6_d_X360",
                "d_mY90": "q6_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_q6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "rr6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q6_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 9),
                "Q": ('con3', 1, 10),
                "mixer": "mixer_rr6",
                "lo_frequency": 7381058000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 20294000.0,
        },
        "q7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q7_grft",
                "X180": "q7_X180",
                "X360": "q7_X360",
                "Y360": "q7_Y360",
                "X90": "q7_X90",
                "mX90": "q7_mX90",
                "Y180": "q7_Y180",
                "Y90": "q7_Y90",
                "mY90": "q7_mY90",
                "I": "zero",
                "d_X180": "q7_d_X180",
                "d_X90": "q7_d_X90",
                "d_mX90": "q7_d_mX90",
                "d_Y180": "q7_d_Y180",
                "d_Y90": "q7_d_Y90",
                "d_Y360": "q7_d_Y360",
                "d_X360": "q7_d_X360",
                "d_mY90": "q7_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_q7",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 125957720.0,
        },
        "rr7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q7_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 9),
                "Q": ('con3', 1, 10),
                "mixer": "mixer_rr7",
                "lo_frequency": 7381058000.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 20544000.0,
        },
        "q8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q8_grft",
                "X180": "q8_X180",
                "X360": "q8_X360",
                "Y360": "q8_Y360",
                "X90": "q8_X90",
                "mX90": "q8_mX90",
                "Y180": "q8_Y180",
                "Y90": "q8_Y90",
                "mY90": "q8_mY90",
                "I": "zero",
                "d_X180": "q8_d_X180",
                "d_X90": "q8_d_X90",
                "d_mX90": "q8_d_mX90",
                "d_Y180": "q8_d_Y180",
                "d_Y90": "q8_d_Y90",
                "d_Y360": "q8_d_Y360",
                "d_X360": "q8_d_X360",
                "d_mY90": "q8_d_mY90",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q8",
                "lo_frequency": 4300000000.0,
            },
            "intermediate_frequency": -140337100.0,
        },
        "rr8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {
                "out1": ('con3', 1, 1),
                "out2": ('con3', 1, 2),
            },
            "operations": {
                "const": "const_pulse",
                "readout": "q8_ro_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 7),
                "Q": ('con3', 1, 8),
                "mixer": "mixer_rr8",
                "lo_frequency": 7395117500.0,
            },
            "smearing": 0,
            "time_of_flight": 300,
            "intermediate_frequency": 20000000.0,
        },
        "cr_c1t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_cr_c1t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "cr_ac_c1t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_cr_ac_c1t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "cr_c1t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_cr_c1t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "cr_ac_c1t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_cr_ac_c1t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "cr_c1t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_cr_c1t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "cr_ac_c1t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_cr_ac_c1t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "cr_c3t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_cr_c3t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "cr_ac_c3t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_cr_ac_c3t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "cr_c3t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_cr_c3t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "cr_ac_c3t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_cr_ac_c3t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "cr_c3t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_cr_c3t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "cr_ac_c3t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_cr_ac_c3t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "cr_c5t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_cr_c5t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "cr_ac_c5t2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_cr_ac_c5t2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 281272650.0,
        },
        "cr_c5t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_cr_c5t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "cr_ac_c5t4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_cr_ac_c5t4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 260657535.0,
        },
        "cr_c5t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_cr_c5t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "cr_ac_c5t6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_cr_ac_c5t6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 148637621.0,
        },
        "q12_1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_1_grft",
                "X180": "q12_1_X180",
                "X360": "q12_1_X360",
                "X90": "q12_1_X90",
                "mX90": "q12_1_mX90",
                "Y180": "q12_1_Y180",
                "Y90": "q12_1_Y90",
                "mY90": "q12_1_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_q12_1",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 116063819.0,
        },
        "q12_2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_2_grft",
                "X180": "q12_2_X180",
                "X360": "q12_2_X360",
                "X90": "q12_2_X90",
                "mX90": "q12_2_mX90",
                "Y180": "q12_2_Y180",
                "Y90": "q12_2_Y90",
                "mY90": "q12_2_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_q12_2",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 12572432.0,
        },
        "q12_3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_3_grft",
                "X180": "q12_3_X180",
                "X360": "q12_3_X360",
                "X90": "q12_3_X90",
                "mX90": "q12_3_mX90",
                "Y180": "q12_3_Y180",
                "Y90": "q12_3_Y90",
                "mY90": "q12_3_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_q12_3",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 102246113.0,
        },
        "q12_4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_4_grft",
                "X180": "q12_4_X180",
                "X360": "q12_4_X360",
                "X90": "q12_4_X90",
                "mX90": "q12_4_mX90",
                "Y180": "q12_4_Y180",
                "Y90": "q12_4_Y90",
                "mY90": "q12_4_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_q12_4",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -21093907.0,
        },
        "q12_5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_5_grft",
                "X180": "q12_5_X180",
                "X360": "q12_5_X360",
                "X90": "q12_5_X90",
                "mX90": "q12_5_mX90",
                "Y180": "q12_5_Y180",
                "Y90": "q12_5_Y90",
                "mY90": "q12_5_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q12_5",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": 51366333.0,
        },
        "q12_6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_6_grft",
                "X180": "q12_6_X180",
                "X360": "q12_6_X360",
                "X90": "q12_6_X90",
                "mX90": "q12_6_mX90",
                "Y180": "q12_6_Y180",
                "Y90": "q12_6_Y90",
                "mY90": "q12_6_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_q12_6",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -146606483.0,
        },
        "q12_7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_7_grft",
                "X180": "q12_7_X180",
                "X360": "q12_7_X360",
                "X90": "q12_7_X90",
                "mX90": "q12_7_mX90",
                "Y180": "q12_7_Y180",
                "Y90": "q12_7_Y90",
                "mY90": "q12_7_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_q12_7",
                "lo_frequency": 4700000000.0,
            },
            "intermediate_frequency": -131548483.0,
        },
        "q12_8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "grft": "q12_8_grft",
                "X180": "q12_8_X180",
                "X360": "q12_8_X360",
                "X90": "q12_8_X90",
                "mX90": "q12_8_mX90",
                "Y180": "q12_8_Y180",
                "Y90": "q12_8_Y90",
                "mY90": "q12_8_mY90",
                "I": "zero",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_q12_8",
                "lo_frequency": 4300000000.0,
            },
            "intermediate_frequency": -204595000.0,
        },
        "stark_1": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 1),
                "Q": ('con1', 1, 2),
                "mixer": "mixer_stark_1",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
        "stark_2": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con1', 1, 3),
                "Q": ('con1', 1, 4),
                "mixer": "mixer_stark_2",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
        "stark_3": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 2),
                "Q": ('con2', 1, 1),
                "mixer": "mixer_stark_3",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
        "stark_4": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con2', 1, 4),
                "Q": ('con2', 1, 3),
                "mixer": "mixer_stark_4",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
        "stark_5": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_stark_5",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
        "stark_6": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": True,
                "digital": False,
                "duration": 320,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 5),
                "Q": ('con3', 1, 6),
                "mixer": "mixer_stark_6",
                "lo_frequency": 4770000000.0,
            },
            "intermediate_frequency": 10000000.0,
        },
        "stark_7": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 3),
                "Q": ('con3', 1, 4),
                "mixer": "mixer_stark_7",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
        "stark_8": {
            "digitalInputs": {},
            "digitalOutputs": {},
            "outputs": {},
            "operations": {
                "const": "const_pulse",
                "rise": "rise_pulse",
                "fall": "fall_pulse",
            },
            "hold_offset": {
                "duration": 0,
            },
            "sticky": {
                "analog": False,
                "digital": False,
                "duration": 4,
            },
            "thread": "",
            "mixInputs": {
                "I": ('con3', 1, 1),
                "Q": ('con3', 1, 2),
                "mixer": "mixer_stark_8",
                "lo_frequency": 40000000000.0,
            },
            "intermediate_frequency": 40000000.0,
        },
    },
    "pulses": {
        "zero": {
            "length": 100,
            "waveforms": {
                "I": "zero_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "const_pulse": {
            "length": 100,
            "waveforms": {
                "I": "const_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_grft": {
            "length": 52,
            "waveforms": {
                "I": "q1_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_X180": {
            "length": 52,
            "waveforms": {
                "I": "q1_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_X360": {
            "length": 52,
            "waveforms": {
                "I": "q1_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_X90": {
            "length": 52,
            "waveforms": {
                "I": "q1_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q1_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q1_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_ro_pulse": {
            "length": 2400,
            "waveforms": {
                "I": "q1_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr1",
                "integW_sin": "integW_sin_rr1",
                "integW_minus_sin": "integW_minus_sin_rr1",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q1_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_X180_I_wf",
                "Q": "q1_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_X90_I_wf",
                "Q": "q1_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_mX90_I_wf",
                "Q": "q1_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y180_I_wf",
                "Q": "q1_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y90_I_wf",
                "Q": "q1_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_Y360_I_wf",
                "Q": "q1_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_X360_I_wf",
                "Q": "q1_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q1_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q1_d_mY90_I_wf",
                "Q": "q1_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_grft": {
            "length": 52,
            "waveforms": {
                "I": "q2_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_X180": {
            "length": 52,
            "waveforms": {
                "I": "q2_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_X360": {
            "length": 52,
            "waveforms": {
                "I": "q2_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_X90": {
            "length": 52,
            "waveforms": {
                "I": "q2_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q2_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q2_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_ro_pulse": {
            "length": 2000,
            "waveforms": {
                "I": "q2_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr2",
                "integW_sin": "integW_sin_rr2",
                "integW_minus_sin": "integW_minus_sin_rr2",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q2_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_X180_I_wf",
                "Q": "q2_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_X90_I_wf",
                "Q": "q2_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_mX90_I_wf",
                "Q": "q2_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y180_I_wf",
                "Q": "q2_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y90_I_wf",
                "Q": "q2_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_Y360_I_wf",
                "Q": "q2_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_X360_I_wf",
                "Q": "q2_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q2_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q2_d_mY90_I_wf",
                "Q": "q2_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_grft": {
            "length": 52,
            "waveforms": {
                "I": "q3_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_X180": {
            "length": 52,
            "waveforms": {
                "I": "q3_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_X360": {
            "length": 52,
            "waveforms": {
                "I": "q3_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_X90": {
            "length": 52,
            "waveforms": {
                "I": "q3_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q3_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q3_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_ro_pulse": {
            "length": 3600,
            "waveforms": {
                "I": "q3_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr3",
                "integW_sin": "integW_sin_rr3",
                "integW_minus_sin": "integW_minus_sin_rr3",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q3_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_X180_I_wf",
                "Q": "q3_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_X90_I_wf",
                "Q": "q3_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_mX90_I_wf",
                "Q": "q3_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_Y180_I_wf",
                "Q": "q3_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_Y90_I_wf",
                "Q": "q3_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_Y360_I_wf",
                "Q": "q3_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_X360_I_wf",
                "Q": "q3_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q3_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q3_d_mY90_I_wf",
                "Q": "q3_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_grft": {
            "length": 52,
            "waveforms": {
                "I": "q4_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_X180": {
            "length": 52,
            "waveforms": {
                "I": "q4_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_X360": {
            "length": 52,
            "waveforms": {
                "I": "q4_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_X90": {
            "length": 52,
            "waveforms": {
                "I": "q4_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q4_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q4_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_ro_pulse": {
            "length": 3600,
            "waveforms": {
                "I": "q4_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr4",
                "integW_sin": "integW_sin_rr4",
                "integW_minus_sin": "integW_minus_sin_rr4",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q4_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_X180_I_wf",
                "Q": "q4_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_X90_I_wf",
                "Q": "q4_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_mX90_I_wf",
                "Q": "q4_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_Y180_I_wf",
                "Q": "q4_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_Y90_I_wf",
                "Q": "q4_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_Y360_I_wf",
                "Q": "q4_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_X360_I_wf",
                "Q": "q4_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q4_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q4_d_mY90_I_wf",
                "Q": "q4_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_grft": {
            "length": 52,
            "waveforms": {
                "I": "q5_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_X180": {
            "length": 52,
            "waveforms": {
                "I": "q5_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_X360": {
            "length": 52,
            "waveforms": {
                "I": "q5_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_Y360": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_X90": {
            "length": 52,
            "waveforms": {
                "I": "q5_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q5_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q5_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_ro_pulse": {
            "length": 2800,
            "waveforms": {
                "I": "q5_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr5",
                "integW_sin": "integW_sin_rr5",
                "integW_minus_sin": "integW_minus_sin_rr5",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q5_d_X180": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_X180_I_wf",
                "Q": "q5_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_X90": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_X90_I_wf",
                "Q": "q5_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_mX90_I_wf",
                "Q": "q5_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_Y180": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_Y180_I_wf",
                "Q": "q5_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_Y90": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_Y90_I_wf",
                "Q": "q5_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_Y360": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_Y360_I_wf",
                "Q": "q5_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_X360": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_X360_I_wf",
                "Q": "q5_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q5_d_mY90": {
            "length": 52,
            "waveforms": {
                "I": "q5_d_mY90_I_wf",
                "Q": "q5_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_grft": {
            "length": 96,
            "waveforms": {
                "I": "q6_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_X180": {
            "length": 96,
            "waveforms": {
                "I": "q6_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_X360": {
            "length": 96,
            "waveforms": {
                "I": "q6_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_Y360": {
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_X90": {
            "length": 96,
            "waveforms": {
                "I": "q6_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_mX90": {
            "length": 96,
            "waveforms": {
                "I": "q6_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_Y180": {
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_Y90": {
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_mY90": {
            "length": 96,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q6_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_ro_pulse": {
            "length": 3200,
            "waveforms": {
                "I": "q6_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr6",
                "integW_sin": "integW_sin_rr6",
                "integW_minus_sin": "integW_minus_sin_rr6",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q6_d_X180": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_X180_I_wf",
                "Q": "q6_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_X90": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_X90_I_wf",
                "Q": "q6_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_mX90": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_mX90_I_wf",
                "Q": "q6_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_Y180": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_Y180_I_wf",
                "Q": "q6_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_Y90": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_Y90_I_wf",
                "Q": "q6_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_Y360": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_Y360_I_wf",
                "Q": "q6_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_X360": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_X360_I_wf",
                "Q": "q6_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q6_d_mY90": {
            "length": 96,
            "waveforms": {
                "I": "q6_d_mY90_I_wf",
                "Q": "q6_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_grft": {
            "length": 512,
            "waveforms": {
                "I": "q7_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_X180": {
            "length": 512,
            "waveforms": {
                "I": "q7_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_X360": {
            "length": 512,
            "waveforms": {
                "I": "q7_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_Y360": {
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_X90": {
            "length": 512,
            "waveforms": {
                "I": "q7_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_mX90": {
            "length": 512,
            "waveforms": {
                "I": "q7_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_Y180": {
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_Y90": {
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_mY90": {
            "length": 512,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q7_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_ro_pulse": {
            "length": 3200,
            "waveforms": {
                "I": "q7_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr7",
                "integW_sin": "integW_sin_rr7",
                "integW_minus_sin": "integW_minus_sin_rr7",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q7_d_X180": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_X180_I_wf",
                "Q": "q7_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_X90": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_X90_I_wf",
                "Q": "q7_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_mX90": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_mX90_I_wf",
                "Q": "q7_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_Y180": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_Y180_I_wf",
                "Q": "q7_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_Y90": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_Y90_I_wf",
                "Q": "q7_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_Y360": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_Y360_I_wf",
                "Q": "q7_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_X360": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_X360_I_wf",
                "Q": "q7_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q7_d_mY90": {
            "length": 512,
            "waveforms": {
                "I": "q7_d_mY90_I_wf",
                "Q": "q7_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_grft": {
            "length": 300,
            "waveforms": {
                "I": "q8_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_X180": {
            "length": 300,
            "waveforms": {
                "I": "q8_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_X360": {
            "length": 300,
            "waveforms": {
                "I": "q8_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_Y360": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_X90": {
            "length": 300,
            "waveforms": {
                "I": "q8_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_mX90": {
            "length": 300,
            "waveforms": {
                "I": "q8_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_Y180": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_Y90": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_mY90": {
            "length": 300,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q8_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_ro_pulse": {
            "length": 2000,
            "waveforms": {
                "I": "q8_ro_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {
                "integW_cos": "integW_cos_rr8",
                "integW_sin": "integW_sin_rr8",
                "integW_minus_sin": "integW_minus_sin_rr8",
            },
            "operation": "measurement",
            "digital_marker": "ON",
        },
        "q8_d_X180": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_X180_I_wf",
                "Q": "q8_d_X180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_X90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_X90_I_wf",
                "Q": "q8_d_X90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_mX90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_mX90_I_wf",
                "Q": "q8_d_mX90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_Y180": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y180_I_wf",
                "Q": "q8_d_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_Y90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y90_I_wf",
                "Q": "q8_d_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_Y360": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_Y360_I_wf",
                "Q": "q8_d_Y360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_X360": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_X360_I_wf",
                "Q": "q8_d_X360_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q8_d_mY90": {
            "length": 300,
            "waveforms": {
                "I": "q8_d_mY90_I_wf",
                "Q": "q8_d_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "rise_pulse": {
            "length": 16,
            "waveforms": {
                "I": "rise_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "fall_pulse": {
            "length": 16,
            "waveforms": {
                "I": "fall_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_1_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_1_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_1_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_2_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_2_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_2_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_3_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_3_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_3_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_3_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_3_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_3_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_3_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_4_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_4_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_4_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_5_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_5_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_5_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_5_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_5_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_5_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_5_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_grft": {
            "length": 104,
            "waveforms": {
                "I": "q12_6_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_X180": {
            "length": 104,
            "waveforms": {
                "I": "q12_6_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_X360": {
            "length": 104,
            "waveforms": {
                "I": "q12_6_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_X90": {
            "length": 104,
            "waveforms": {
                "I": "q12_6_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q12_6_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_Y180": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_Y90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_6_mY90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_6_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_grft": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_X180": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_X360": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_X90": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_mX90": {
            "length": 104,
            "waveforms": {
                "I": "q12_7_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_Y180": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_Y90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_7_mY90": {
            "length": 104,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_7_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_grft": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_grft_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_X180": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_X180_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_X360": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_X360_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_X90": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_X90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_mX90": {
            "length": 52,
            "waveforms": {
                "I": "q12_8_mX90_I_wf",
                "Q": "zero_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_Y180": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y180_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_Y90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_Y90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
        "q12_8_mY90": {
            "length": 52,
            "waveforms": {
                "I": "zero_wf",
                "Q": "q12_8_mY90_Q_wf",
            },
            "integration_weights": {},
            "operation": "control",
        },
    },
    "waveforms": {
        "zero_wf": {
            "type": "constant",
            "sample": 0.0,
        },
        "const_wf": {
            "type": "constant",
            "sample": 0.4,
        },
        "q1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0018102325287692638, 0.0049207221882389554, 0.01196928990414829, 0.026052714666758268, 0.05074375921832951, 0.08844175456611598, 0.13793583859088626, 0.1925049702021102, 0.24040961431410787, 0.26866232830489245] + [0.27241978256242366] * 32 + [0.26866232830489245, 0.24040961431410787, 0.1925049702021102, 0.13793583859088626, 0.08844175456611598, 0.05074375921832951, 0.026052714666758268, 0.01196928990414829, 0.0049207221882389554, 0.0018102325287692638],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009016360704760211, 0.002450900946258187, 0.005961633847615021, 0.012976270674651555, 0.025274324118958358, 0.044050846941311166, 0.06870273597914867, 0.09588239196990901, 0.11974261676879687, 0.13381465758017974] + [0.13568616095773597] * 32 + [0.13381465758017974, 0.11974261676879687, 0.09588239196990901, 0.06870273597914867, 0.044050846941311166, 0.025274324118958358, 0.012976270674651555, 0.005961633847615021, 0.002450900946258187, 0.0009016360704760211],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0009016360704760211, -0.002450900946258187, -0.005961633847615021, -0.012976270674651555, -0.025274324118958358, -0.044050846941311166, -0.06870273597914867, -0.09588239196990901, -0.11974261676879687, -0.13381465758017974] + [-0.13568616095773597] * 32 + [-0.13381465758017974, -0.11974261676879687, -0.09588239196990901, -0.06870273597914867, -0.044050846941311166, -0.025274324118958358, -0.012976270674651555, -0.005961633847615021, -0.002450900946258187, -0.0009016360704760211],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0018131326903597729, 0.004928605644790031, 0.011988465824530895, 0.02609445354903125, 0.05082505546016817, 0.08858344651757166, 0.1381568246877983, 0.19281338114473193, 0.24079477297098875, 0.2690927504484478] + [0.27285622449865354] * 32 + [0.2690927504484478, 0.24079477297098875, 0.19281338114473193, 0.1381568246877983, 0.08858344651757166, 0.05082505546016817, 0.02609445354903125, 0.011988465824530895, 0.004928605644790031, 0.0018131326903597729],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000892645569545443, 0.0024264622309498524, 0.005902188494428949, 0.012846880139605308, 0.025022305769258506, 0.04361160189179854, 0.06801767907872132, 0.09492631804778165, 0.1185486249324661, 0.13248034893515798] + [0.13433319095542334] * 32 + [0.13248034893515798, 0.1185486249324661, 0.09492631804778165, 0.06801767907872132, 0.04361160189179854, 0.025022305769258506, 0.012846880139605308, 0.005902188494428949, 0.0024264622309498524, 0.000892645569545443],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000892645569545443, -0.0024264622309498524, -0.005902188494428949, -0.012846880139605308, -0.025022305769258506, -0.04361160189179854, -0.06801767907872132, -0.09492631804778165, -0.1185486249324661, -0.13248034893515798] + [-0.13433319095542334] * 32 + [-0.13248034893515798, -0.1185486249324661, -0.09492631804778165, -0.06801767907872132, -0.04361160189179854, -0.025022305769258506, -0.012846880139605308, -0.005902188494428949, -0.0024264622309498524, -0.000892645569545443],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0005187064943764417, 0.0005429527587189518, 0.0005682019271479149, 0.0005944887771340143, 0.0006218489681410942, 0.0006503190489357455, 0.0006799364641902206, 0.0007107395603368492, 0.0007427675906314458, 0.0007760607193825638, 0.0008106600253028521, 0.0008466075039382395, 0.0008839460691301981, 0.0009227195534659253, 0.000962972707670938, 0.0010047511988982892, 0.0010481016078684325, 0.0010930714248136078, 0.0011397090441806173, 0.00118806375804585, 0.0012381857481965986, 0.0012901260768328838, 0.001343936675844356, 0.001399670334617225, 0.0014573806863267236, 0.001517122192671188, 0.0015789501270046106, 0.0016429205558253315, 0.001709090318579508, 0.0017775170057390559, 0.0018482589351149718, 0.0019213751263682357, 0.001996925273681932, 0.0020749697165598096, 0.0021555694087181548, 0.0022387858850397083, 0.0023246812265602704, 0.002413318023460737, 0.002504759336039516, 0.0025990686536426105, 0.002696309851531143, 0.002796547145668675, 0.0028998450454134615, 0.003006268304103581, 0.0031158818675259786, 0.00322875082026346, 0.0033449403299170726, 0.003464515589204558, 0.0035875417559391547, 0.0037140838908965926, 0.003844206893581887, 0.003977975435911384, 0.004115453893829432, 0.004256706276883158, 0.004401796155782963, 0.004550786587980574, 0.0047037400413008894, 0.0048607183156681895, 0.005021782462971869, 0.005186992705121326, 0.00535640835034431, 0.005530087707787693, 0.005708088000484348, 0.0058904652767545725, 0.0060772743201152725, 0.0062685685577749325, 0.006464399967797199, 0.00666481898502072, 0.006869874405827684, 0.007079613291858256, 0.007294080872772903, 0.007513320448169221, 0.007737373288764626, 0.007966278536960766, 0.00820007310691006, 0.00843879158420916, 0.008682466125348514, 0.00893112635705128, 0.00918479927563906, 0.009443509146565776, 0.009707277404264818, 0.009976122552458232, 0.01025006006508018, 0.010529102287970132, 0.010813258341494367, 0.01110253402425719, 0.011396931718065948, 0.01169645029431623, 0.012001085021965981, 0.012310827477268957, 0.01262566545543974, 0.012945582884423795, 0.013270559740947225, 0.013600571969021494, 0.013935591401079082, 0.014275585681915955, 0.014620518195616751, 0.01497034799563796, 0.015325029738223628, 0.015684513619326875, 0.01604874531520895, 0.016417665926885826, 0.016791211928589855, 0.01716931512041152, 0.01755190258528343, 0.017938896650465122, 0.01833021485368369, 0.018725769914081154, 0.019125469708114917, 0.019529217250552962, 0.019936910680700123, 0.020348443253986236, 0.02076370333904112, 0.021182574420374876, 0.02160493510677562, 0.022030659145529444, 0.02245961544256044, 0.022891668088580716, 0.02332667639133243, 0.023764494913995703, 0.02420497351982752, 0.02464795742308804, 0.02509328724630143, 0.025540799083889155, 0.025990324572203818, 0.026441690965981892, 0.026894721221223602, 0.027349234084497978, 0.027805044188660435, 0.028261962154960064, 0.028719794701502533, 0.029178344758024135, 0.029637411586921195, 0.0300967909104682, 0.030556275044146874, 0.031015653035997282, 0.031474710811890856, 0.03193323132661429, 0.032390994720641934, 0.032847778482463424, 0.033303357616322325, 0.0337575048152107, 0.034209990638953774, 0.03466058369720844, 0.03510905083718876, 0.03555515733592173, 0.03599866709682636, 0.036439342850399604, 0.036876946358783184, 0.037311238623976305, 0.03774198009945037, 0.038168930904913356, 0.038591851043963565, 0.03901050062436454, 0.03942464008066584, 0.03983403039888727, 0.04023843334297811, 0.04063761168275637, 0.0410313294230282, 0.04141935203358215, 0.04180144667974872, 0.04217738245321173, 0.04254693060275434, 0.04290986476462021, 0.043265961192167315, 0.04361499898449094, 0.043956760313690696, 0.04429103065045601, 0.04461759898764486, 0.04493625806153063, 0.04524680457039379, 0.04554903939013658, 0.04584276778660145, 0.04612779962427714, 0.046403949571079926, 0.04667103729890175, 0.04692888767962196, 0.04717733097628471, 0.04741620302915028, 0.04764534543633499, 0.0478646057287616, 0.04807383753915013, 0.04827290076478668, 0.04846166172381721, 0.048639993304822174, 0.048807775109437825, 0.04896489358780022, 0.0491112421665986, 0.049246721369536145, 0.04937123893000731, 0.049484709895813384, 0.049587056725749507, 0.049678209377909864, 0.04975810538956994, 0.04982668994851846, 0.0498839159557249, 0.04992974407924243, 0.049964142799259675, 0.04998708844422928, 0.049998565218015226] + [0.05] * 2000 + [0.049998565218015226, 0.04998708844422928, 0.049964142799259675, 0.04992974407924243, 0.0498839159557249, 0.04982668994851846, 0.04975810538956994, 0.049678209377909864, 0.049587056725749507, 0.049484709895813384, 0.04937123893000731, 0.049246721369536145, 0.0491112421665986, 0.04896489358780022, 0.048807775109437825, 0.048639993304822174, 0.04846166172381721, 0.04827290076478668, 0.04807383753915013, 0.0478646057287616, 0.04764534543633499, 0.04741620302915028, 0.04717733097628471, 0.04692888767962196, 0.04667103729890175, 0.046403949571079926, 0.04612779962427714, 0.04584276778660145, 0.04554903939013658, 0.04524680457039379, 0.04493625806153063, 0.04461759898764486, 0.04429103065045601, 0.043956760313690696, 0.04361499898449094, 0.043265961192167315, 0.04290986476462021, 0.04254693060275434, 0.04217738245321173, 0.04180144667974872, 0.04141935203358215, 0.0410313294230282, 0.04063761168275637, 0.04023843334297811, 0.03983403039888727, 0.03942464008066584, 0.03901050062436454, 0.038591851043963565, 0.038168930904913356, 0.03774198009945037, 0.037311238623976305, 0.036876946358783184, 0.036439342850399604, 0.03599866709682636, 0.03555515733592173, 0.03510905083718876, 0.03466058369720844, 0.034209990638953774, 0.0337575048152107, 0.033303357616322325, 0.032847778482463424, 0.032390994720641934, 0.03193323132661429, 0.031474710811890856, 0.031015653035997282, 0.030556275044146874, 0.0300967909104682, 0.029637411586921195, 0.029178344758024135, 0.028719794701502533, 0.028261962154960064, 0.027805044188660435, 0.027349234084497978, 0.026894721221223602, 0.026441690965981892, 0.025990324572203818, 0.025540799083889155, 0.02509328724630143, 0.02464795742308804, 0.02420497351982752, 0.023764494913995703, 0.02332667639133243, 0.022891668088580716, 0.02245961544256044, 0.022030659145529444, 0.02160493510677562, 0.021182574420374876, 0.02076370333904112, 0.020348443253986236, 0.019936910680700123, 0.019529217250552962, 0.019125469708114917, 0.018725769914081154, 0.01833021485368369, 0.017938896650465122, 0.01755190258528343, 0.01716931512041152, 0.016791211928589855, 0.016417665926885826, 0.01604874531520895, 0.015684513619326875, 0.015325029738223628, 0.01497034799563796, 0.014620518195616751, 0.014275585681915955, 0.013935591401079082, 0.013600571969021494, 0.013270559740947225, 0.012945582884423795, 0.01262566545543974, 0.012310827477268957, 0.012001085021965981, 0.01169645029431623, 0.011396931718065948, 0.01110253402425719, 0.010813258341494367, 0.010529102287970132, 0.01025006006508018, 0.009976122552458232, 0.009707277404264818, 0.009443509146565776, 0.00918479927563906, 0.00893112635705128, 0.008682466125348514, 0.00843879158420916, 0.00820007310691006, 0.007966278536960766, 0.007737373288764626, 0.007513320448169221, 0.007294080872772903, 0.007079613291858256, 0.006869874405827684, 0.00666481898502072, 0.006464399967797199, 0.0062685685577749325, 0.0060772743201152725, 0.0058904652767545725, 0.005708088000484348, 0.005530087707787693, 0.00535640835034431, 0.005186992705121326, 0.005021782462971869, 0.0048607183156681895, 0.0047037400413008894, 0.004550786587980574, 0.004401796155782963, 0.004256706276883158, 0.004115453893829432, 0.003977975435911384, 0.003844206893581887, 0.0037140838908965926, 0.0035875417559391547, 0.003464515589204558, 0.0033449403299170726, 0.00322875082026346, 0.0031158818675259786, 0.003006268304103581, 0.0028998450454134615, 0.002796547145668675, 0.002696309851531143, 0.0025990686536426105, 0.002504759336039516, 0.002413318023460737, 0.0023246812265602704, 0.0022387858850397083, 0.0021555694087181548, 0.0020749697165598096, 0.001996925273681932, 0.0019213751263682357, 0.0018482589351149718, 0.0017775170057390559, 0.001709090318579508, 0.0016429205558253315, 0.0015789501270046106, 0.001517122192671188, 0.0014573806863267236, 0.001399670334617225, 0.001343936675844356, 0.0012901260768328838, 0.0012381857481965986, 0.00118806375804585, 0.0011397090441806173, 0.0010930714248136078, 0.0010481016078684325, 0.0010047511988982892, 0.000962972707670938, 0.0009227195534659253, 0.0008839460691301981, 0.0008466075039382395, 0.0008106600253028521, 0.0007760607193825638, 0.0007427675906314458, 0.0007107395603368492, 0.0006799364641902206, 0.0006503190489357455, 0.0006218489681410942, 0.0005944887771340143, 0.0005682019271479149, 0.0005429527587189518, 0.0005187064943764417],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0018102325287692638, 0.0049207221882389554, 0.01196928990414829, 0.026052714666758268, 0.05074375921832951, 0.08844175456611598, 0.13793583859088626, 0.1925049702021102, 0.24040961431410787, 0.26866232830489245] + [0.27241978256242366] * 32 + [0.26866232830489245, 0.24040961431410787, 0.1925049702021102, 0.13793583859088626, 0.08844175456611598, 0.05074375921832951, 0.026052714666758268, 0.01196928990414829, 0.0049207221882389554, 0.0018102325287692638],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000745215354671824, -0.0018124732140622308, -0.0038900346892047533, -0.007338210481279233, -0.012093977377148428, -0.017246210727192103, -0.0209203520515165, -0.020854788043051208, -0.01562668707650058, -0.0058210402630838156] + [0.0] * 32 + [0.0058210402630838156, 0.01562668707650058, 0.020854788043051208, 0.0209203520515165, 0.017246210727192103, 0.012093977377148428, 0.007338210481279233, 0.0038900346892047533, 0.0018124732140622308, 0.000745215354671824],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009016360704760211, 0.002450900946258187, 0.005961633847615021, 0.012976270674651555, 0.025274324118958358, 0.044050846941311166, 0.06870273597914867, 0.09588239196990901, 0.11974261676879687, 0.13381465758017974] + [0.13568616095773597] * 32 + [0.13381465758017974, 0.11974261676879687, 0.09588239196990901, 0.06870273597914867, 0.044050846941311166, 0.025274324118958358, 0.012976270674651555, 0.005961633847615021, 0.002450900946258187, 0.0009016360704760211],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0003711749918125249, -0.0009027521053779559, -0.0019375387059112137, -0.0036549974423257634, -0.006023737870941716, -0.008589949315096471, -0.010419956396170008, -0.010387300439535813, -0.007783301043536984, -0.002899329111303676] + [0.0] * 32 + [0.002899329111303676, 0.007783301043536984, 0.010387300439535813, 0.010419956396170008, 0.008589949315096471, 0.006023737870941716, 0.0036549974423257634, 0.0019375387059112137, 0.0009027521053779559, 0.0003711749918125249],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0009016360704760211, -0.002450900946258187, -0.005961633847615021, -0.012976270674651555, -0.025274324118958358, -0.044050846941311166, -0.06870273597914867, -0.09588239196990901, -0.11974261676879687, -0.13381465758017974] + [-0.13568616095773597] * 32 + [-0.13381465758017974, -0.11974261676879687, -0.09588239196990901, -0.06870273597914867, -0.044050846941311166, -0.025274324118958358, -0.012976270674651555, -0.005961633847615021, -0.002450900946258187, -0.0009016360704760211],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003711749918125249, 0.0009027521053779559, 0.0019375387059112137, 0.0036549974423257634, 0.006023737870941716, 0.008589949315096471, 0.010419956396170008, 0.010387300439535813, 0.007783301043536984, 0.002899329111303676] + [0.0] * 32 + [-0.002899329111303676, -0.007783301043536984, -0.010387300439535813, -0.010419956396170008, -0.008589949315096471, -0.006023737870941716, -0.0036549974423257634, -0.0019375387059112137, -0.0009027521053779559, -0.0003711749918125249],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007464092592746466, 0.0018153769654398635, 0.003896266888114055, 0.007349966979874109, 0.012113353058508842, 0.017273840767608423, 0.020953868409506696, 0.020888199361376036, 0.01565172248876167, 0.005830366113282343] + [0.0] * 32 + [-0.005830366113282343, -0.01565172248876167, -0.020888199361376036, -0.020953868409506696, -0.017273840767608423, -0.012113353058508842, -0.007349966979874109, -0.003896266888114055, -0.0018153769654398635, -0.0007464092592746466],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0018131326903597729, 0.004928605644790031, 0.011988465824530895, 0.02609445354903125, 0.05082505546016817, 0.08858344651757166, 0.1381568246877983, 0.19281338114473193, 0.24079477297098875, 0.2690927504484478] + [0.27285622449865354] * 32 + [0.2690927504484478, 0.24079477297098875, 0.19281338114473193, 0.1381568246877983, 0.08858344651757166, 0.05082505546016817, 0.02609445354903125, 0.011988465824530895, 0.004928605644790031, 0.0018131326903597729],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00036747388754377485, 0.0008937504761072936, 0.0019182188892923765, 0.0036185522966816434, 0.00596367325872443, 0.008504296189805886, 0.010316055686400389, 0.010283725352728852, 0.00770569126552761, 0.002870418975688243] + [0.0] * 32 + [-0.002870418975688243, -0.00770569126552761, -0.010283725352728852, -0.010316055686400389, -0.008504296189805886, -0.00596367325872443, -0.0036185522966816434, -0.0019182188892923765, -0.0008937504761072936, -0.00036747388754377485],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000892645569545443, 0.0024264622309498524, 0.005902188494428949, 0.012846880139605308, 0.025022305769258506, 0.04361160189179854, 0.06801767907872132, 0.09492631804778165, 0.1185486249324661, 0.13248034893515798] + [0.13433319095542334] * 32 + [0.13248034893515798, 0.1185486249324661, 0.09492631804778165, 0.06801767907872132, 0.04361160189179854, 0.025022305769258506, 0.012846880139605308, 0.005902188494428949, 0.0024264622309498524, 0.000892645569545443],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002552277098571049, 0.0006207512831054925, 0.001332292254535805, 0.002513252905814174, 0.004142048509444026, 0.005906629325361513, 0.007164980579156634, 0.007142525658408233, 0.0053519610541911695, 0.0019936395110741463] + [0.0] * 32 + [-0.0019936395110741463, -0.0053519610541911695, -0.007142525658408233, -0.007164980579156634, -0.005906629325361513, -0.004142048509444026, -0.002513252905814174, -0.001332292254535805, -0.0006207512831054925, -0.0002552277098571049],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002552277098571049, -0.0006207512831054925, -0.001332292254535805, -0.002513252905814174, -0.004142048509444026, -0.005906629325361513, -0.007164980579156634, -0.007142525658408233, -0.0053519610541911695, -0.0019936395110741463] + [0.0] * 32 + [0.0019936395110741463, 0.0053519610541911695, 0.007142525658408233, 0.007164980579156634, 0.005906629325361513, 0.004142048509444026, 0.002513252905814174, 0.001332292254535805, 0.0006207512831054925, 0.0002552277098571049],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00036747388754377485, -0.0008937504761072936, -0.0019182188892923765, -0.0036185522966816434, -0.00596367325872443, -0.008504296189805886, -0.010316055686400389, -0.010283725352728852, -0.00770569126552761, -0.002870418975688243] + [0.0] * 32 + [0.002870418975688243, 0.00770569126552761, 0.010283725352728852, 0.010316055686400389, 0.008504296189805886, 0.00596367325872443, 0.0036185522966816434, 0.0019182188892923765, 0.0008937504761072936, 0.00036747388754377485],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q1_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000892645569545443, -0.0024264622309498524, -0.005902188494428949, -0.012846880139605308, -0.025022305769258506, -0.04361160189179854, -0.06801767907872132, -0.09492631804778165, -0.1185486249324661, -0.13248034893515798] + [-0.13433319095542334] * 32 + [-0.13248034893515798, -0.1185486249324661, -0.09492631804778165, -0.06801767907872132, -0.04361160189179854, -0.025022305769258506, -0.012846880139605308, -0.005902188494428949, -0.0024264622309498524, -0.000892645569545443],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001728015332229015, 0.004697232676896751, 0.011425668327993303, 0.024869451672572557, 0.04843907760503372, 0.08442490424331768, 0.13167106444108065, 0.18376177355828333, 0.22949068307400539, 0.2564602144337967] + [0.2600470125185585] * 32 + [0.2564602144337967, 0.22949068307400539, 0.18376177355828333, 0.13167106444108065, 0.08442490424331768, 0.04843907760503372, 0.024869451672572557, 0.011425668327993303, 0.004697232676896751, 0.001728015332229015],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0023019196663695667, 0.006257266399664901, 0.015220334064800986, 0.03312903469616625, 0.06452654862500447, 0.11246390224927966, 0.1754013445805286, 0.24479229587339238, 0.30570858184181127, 0.3416351696862567] + [0.34641320660330166] * 32 + [0.3416351696862567, 0.30570858184181127, 0.24479229587339238, 0.1754013445805286, 0.11246390224927966, 0.06452654862500447, 0.03312903469616625, 0.015220334064800986, 0.006257266399664901, 0.0023019196663695667],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0023019196663695667, 0.006257266399664901, 0.015220334064800986, 0.03312903469616625, 0.06452654862500447, 0.11246390224927966, 0.1754013445805286, 0.24479229587339238, 0.30570858184181127, 0.3416351696862567] + [0.34641320660330166] * 32 + [0.3416351696862567, 0.30570858184181127, 0.24479229587339238, 0.1754013445805286, 0.11246390224927966, 0.06452654862500447, 0.03312903469616625, 0.015220334064800986, 0.006257266399664901, 0.0023019196663695667],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008599720895460722, 0.002337646503995043, 0.005686150859443048, 0.012376646156917807, 0.024106415033917344, 0.042015287687407414, 0.06552802993598945, 0.0914517327700801, 0.11420939303815864, 0.1276311745495765] + [0.1294161970468906] * 32 + [0.1276311745495765, 0.11420939303815864, 0.0914517327700801, 0.06552802993598945, 0.042015287687407414, 0.024106415033917344, 0.012376646156917807, 0.005686150859443048, 0.002337646503995043, 0.0008599720895460722],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008599720895460722, -0.002337646503995043, -0.005686150859443048, -0.012376646156917807, -0.024106415033917344, -0.042015287687407414, -0.06552802993598945, -0.0914517327700801, -0.11420939303815864, -0.1276311745495765] + [-0.1294161970468906] * 32 + [-0.1276311745495765, -0.11420939303815864, -0.0914517327700801, -0.06552802993598945, -0.042015287687407414, -0.024106415033917344, -0.012376646156917807, -0.005686150859443048, -0.002337646503995043, -0.0008599720895460722],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0017221707040954192, 0.004681345330447098, 0.011387023542088086, 0.024785336274866496, 0.04827524318154477, 0.08413935575233286, 0.13122571630483457, 0.18314024016584937, 0.22871448179981746, 0.25559279470870994] + [0.25916746124544393] * 32 + [0.25559279470870994, 0.22871448179981746, 0.18314024016584937, 0.13122571630483457, 0.08413935575233286, 0.04827524318154477, 0.024785336274866496, 0.011387023542088086, 0.004681345330447098, 0.0017221707040954192],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008570497754792741, 0.0023297028307702155, 0.005666828466490438, 0.01233458845806477, 0.024024497822172863, 0.04187251344191499, 0.0653053558678664, 0.09114096607386311, 0.11382129240106464, 0.1271974646870331] + [0.1289764214103333] * 32 + [0.1271974646870331, 0.11382129240106464, 0.09114096607386311, 0.0653053558678664, 0.04187251344191499, 0.024024497822172863, 0.01233458845806477, 0.005666828466490438, 0.0023297028307702155, 0.0008570497754792741],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008570497754792741, -0.0023297028307702155, -0.005666828466490438, -0.01233458845806477, -0.024024497822172863, -0.04187251344191499, -0.0653053558678664, -0.09114096607386311, -0.11382129240106464, -0.1271974646870331] + [-0.1289764214103333] * 32 + [-0.1271974646870331, -0.11382129240106464, -0.09114096607386311, -0.0653053558678664, -0.04187251344191499, -0.024024497822172863, -0.01233458845806477, -0.005666828466490438, -0.0023297028307702155, -0.0008570497754792741],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0016598607820046136, 0.001737448827900646, 0.001818246166873328, 0.001902364086828846, 0.001989916698051502, 0.002081020956594386, 0.002175796685408706, 0.002274366593077918, 0.002376856290020627, 0.002483394302024204, 0.0025941120809691268, 0.0027091440126023668, 0.0028286274212166347, 0.0029527025710909616, 0.003081512664547002, 0.003215203836474526, 0.0033539251451789845, 0.0034978285594035458, 0.003647068941377976, 0.003801804025746721, 0.003962194394229116, 0.0041284034458652285, 0.004300597362701939, 0.00447894507077512, 0.004663618196245516, 0.004854791016547802, 0.005052640406414754, 0.005257345778641061, 0.005469089019454426, 0.0056880544183649795, 0.005914428592367911, 0.006148400404378355, 0.006390160875782183, 0.0066399030929913914, 0.006897822107898096, 0.007164114832127068, 0.007438979924992866, 0.0077226176750743595, 0.008015229875326452, 0.008317019691656356, 0.008628191524899659, 0.008948950866139761, 0.009279504145323077, 0.009620058573131461, 0.009970821976083132, 0.010332002624843073, 0.010703809055734634, 0.011086449885454588, 0.011480133619005297, 0.0118850684508691, 0.01230146205946204, 0.012729521394916432, 0.013169452460254185, 0.013621460086026108, 0.014085747698505485, 0.014562517081537838, 0.015051968132162847, 0.01555429861013821, 0.016069703881509984, 0.016598376656388247, 0.017140506721101796, 0.01769628066492062, 0.018265881601549915, 0.018849488885614635, 0.019447277824368874, 0.02005941938487979, 0.02068607989695104, 0.021327420752066305, 0.021983598098648593, 0.022654762533946424, 0.023341058792873293, 0.024042625434141512, 0.024759594524046805, 0.025492091318274457, 0.026240233942112196, 0.027004133069469315, 0.027783891601115253, 0.028579604342564104, 0.029391357682045, 0.030219229269010488, 0.031063287693647423, 0.031923592167866346, 0.03280019220825658, 0.033693127321504424, 0.034602426692781976, 0.03552810887762301, 0.03647018149781104, 0.03742864094181194, 0.03840347207029115, 0.03939464792726067, 0.04040212945740717, 0.04142586523015615, 0.04246579117103112, 0.043521830300868786, 0.044593892483453065, 0.04568187418213106, 0.04678565822597361, 0.04790511358604148, 0.04904009516231562, 0.050190443581846, 0.05135598500866864, 0.05253653096603466, 0.053731878171487536, 0.05494180838531687, 0.056166088272906985, 0.0574044692814884, 0.05865668753178782, 0.0599224637250597, 0.061201503065967736, 0.062493495201769486, 0.0637981141782404, 0.06511501841275597, 0.06644385068493158, 0.06778423814519961, 0.06913579234168199, 0.07049810926569422, 0.07187076941619341, 0.0732533378834583, 0.07464536445226377, 0.07604638372478625, 0.07745591526344807, 0.07887346375388174, 0.08029851918816458, 0.08173055706844531, 0.08316903863105223, 0.08461341109114207, 0.08606310790791553, 0.08751754907039354, 0.0889761414037134, 0.09043827889587222, 0.09190334304480813, 0.09337070322567724, 0.09483971707814783, 0.09630973091349825, 0.09778008014127001, 0.09925008971519132, 0.10071907459805075, 0.10218634024516575, 0.10365118310605421, 0.10511289114388297, 0.10657074437223146, 0.10802401540867426, 0.1094719700446521, 0.11091386783106702, 0.11234896267900406, 0.11377650347494955, 0.11519573470984437, 0.11660589712127875, 0.1180062283481062, 0.11939596359672419, 0.1207743363182412, 0.12214057889572276, 0.12349392334068343, 0.12483360199796656, 0.1261588482581307, 0.12746889727643929, 0.12876298669752995, 0.13004035738482042, 0.13130025415369026, 0.13254192650746288, 0.13376462937519593, 0.13496762385027755, 0.13615017792881393, 0.1373115672467847, 0.13845107581493543, 0.13956799675037102, 0.14066163300381024, 0.14173129808145926, 0.14277631676046357, 0.14379602579689804, 0.14478977462526016, 0.1457569260484371, 0.14669685691712467, 0.14760895879768687, 0.1484926386274558, 0.14934731935648562, 0.1501724405747903, 0.15096745912411108, 0.15173184969328093, 0.15246510539627198, 0.15316673833203714, 0.15383628012528044, 0.1544732824473174, 0.1550773175162151, 0.15564797857543097, 0.15618488035020106, 0.15668765948096072, 0.15715597493311556, 0.15758950838251568, 0.15798796457602343, 0.15835107166660284, 0.15867858152239844, 0.15897027000931158, 0.15922593724662384, 0.1594454078352591, 0.1596285310583197, 0.1597751810535758, 0.15988525695763098, 0.1599586830215337, 0.15999540869764875] + [0.16000000000000003] * 1600 + [0.15999540869764875, 0.1599586830215337, 0.15988525695763098, 0.1597751810535758, 0.1596285310583197, 0.1594454078352591, 0.15922593724662384, 0.15897027000931158, 0.15867858152239844, 0.15835107166660284, 0.15798796457602343, 0.15758950838251568, 0.15715597493311556, 0.15668765948096072, 0.15618488035020106, 0.15564797857543097, 0.1550773175162151, 0.1544732824473174, 0.15383628012528044, 0.15316673833203714, 0.15246510539627198, 0.15173184969328093, 0.15096745912411108, 0.1501724405747903, 0.14934731935648562, 0.1484926386274558, 0.14760895879768687, 0.14669685691712467, 0.1457569260484371, 0.14478977462526016, 0.14379602579689804, 0.14277631676046357, 0.14173129808145926, 0.14066163300381024, 0.13956799675037102, 0.13845107581493543, 0.1373115672467847, 0.13615017792881393, 0.13496762385027755, 0.13376462937519593, 0.13254192650746288, 0.13130025415369026, 0.13004035738482042, 0.12876298669752995, 0.12746889727643929, 0.1261588482581307, 0.12483360199796656, 0.12349392334068343, 0.12214057889572276, 0.1207743363182412, 0.11939596359672419, 0.1180062283481062, 0.11660589712127875, 0.11519573470984437, 0.11377650347494955, 0.11234896267900406, 0.11091386783106702, 0.1094719700446521, 0.10802401540867426, 0.10657074437223146, 0.10511289114388297, 0.10365118310605421, 0.10218634024516575, 0.10071907459805075, 0.09925008971519132, 0.09778008014127001, 0.09630973091349825, 0.09483971707814783, 0.09337070322567724, 0.09190334304480813, 0.09043827889587222, 0.0889761414037134, 0.08751754907039354, 0.08606310790791553, 0.08461341109114207, 0.08316903863105223, 0.08173055706844531, 0.08029851918816458, 0.07887346375388174, 0.07745591526344807, 0.07604638372478625, 0.07464536445226377, 0.0732533378834583, 0.07187076941619341, 0.07049810926569422, 0.06913579234168199, 0.06778423814519961, 0.06644385068493158, 0.06511501841275597, 0.0637981141782404, 0.062493495201769486, 0.061201503065967736, 0.0599224637250597, 0.05865668753178782, 0.0574044692814884, 0.056166088272906985, 0.05494180838531687, 0.053731878171487536, 0.05253653096603466, 0.05135598500866864, 0.050190443581846, 0.04904009516231562, 0.04790511358604148, 0.04678565822597361, 0.04568187418213106, 0.044593892483453065, 0.043521830300868786, 0.04246579117103112, 0.04142586523015615, 0.04040212945740717, 0.03939464792726067, 0.03840347207029115, 0.03742864094181194, 0.03647018149781104, 0.03552810887762301, 0.034602426692781976, 0.033693127321504424, 0.03280019220825658, 0.031923592167866346, 0.031063287693647423, 0.030219229269010488, 0.029391357682045, 0.028579604342564104, 0.027783891601115253, 0.027004133069469315, 0.026240233942112196, 0.025492091318274457, 0.024759594524046805, 0.024042625434141512, 0.023341058792873293, 0.022654762533946424, 0.021983598098648593, 0.021327420752066305, 0.02068607989695104, 0.02005941938487979, 0.019447277824368874, 0.018849488885614635, 0.018265881601549915, 0.01769628066492062, 0.017140506721101796, 0.016598376656388247, 0.016069703881509984, 0.01555429861013821, 0.015051968132162847, 0.014562517081537838, 0.014085747698505485, 0.013621460086026108, 0.013169452460254185, 0.012729521394916432, 0.01230146205946204, 0.0118850684508691, 0.011480133619005297, 0.011086449885454588, 0.010703809055734634, 0.010332002624843073, 0.009970821976083132, 0.009620058573131461, 0.009279504145323077, 0.008948950866139761, 0.008628191524899659, 0.008317019691656356, 0.008015229875326452, 0.0077226176750743595, 0.007438979924992866, 0.007164114832127068, 0.006897822107898096, 0.0066399030929913914, 0.006390160875782183, 0.006148400404378355, 0.005914428592367911, 0.0056880544183649795, 0.005469089019454426, 0.005257345778641061, 0.005052640406414754, 0.004854791016547802, 0.004663618196245516, 0.00447894507077512, 0.004300597362701939, 0.0041284034458652285, 0.003962194394229116, 0.003801804025746721, 0.003647068941377976, 0.0034978285594035458, 0.0033539251451789845, 0.003215203836474526, 0.003081512664547002, 0.0029527025710909616, 0.0028286274212166347, 0.0027091440126023668, 0.0025941120809691268, 0.002483394302024204, 0.002376856290020627, 0.002274366593077918, 0.002175796685408706, 0.002081020956594386, 0.001989916698051502, 0.001902364086828846, 0.001818246166873328, 0.001737448827900646, 0.0016598607820046136],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001728015332229015, 0.004697232676896751, 0.011425668327993303, 0.024869451672572557, 0.04843907760503372, 0.08442490424331768, 0.13167106444108065, 0.18376177355828333, 0.22949068307400539, 0.2564602144337967] + [0.2600470125185585] * 32 + [0.2564602144337967, 0.22949068307400539, 0.18376177355828333, 0.13167106444108065, 0.08442490424331768, 0.04843907760503372, 0.024869451672572557, 0.011425668327993303, 0.004697232676896751, 0.001728015332229015],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006305845515305529, 0.001533674261655393, 0.003291660275855047, 0.0062094294439384605, 0.01023365293371905, 0.014593357462148685, 0.0177023336053996, 0.01764685480908194, 0.013222952801855325, 0.004925633967048994] + [0.0] * 32 + [-0.004925633967048994, -0.013222952801855325, -0.01764685480908194, -0.0177023336053996, -0.014593357462148685, -0.01023365293371905, -0.0062094294439384605, -0.003291660275855047, -0.001533674261655393, -0.0006305845515305529],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008599720895460722, 0.002337646503995043, 0.005686150859443048, 0.012376646156917807, 0.024106415033917344, 0.042015287687407414, 0.06552802993598945, 0.0914517327700801, 0.11420939303815864, 0.1276311745495765] + [0.1294161970468906] * 32 + [0.1276311745495765, 0.11420939303815864, 0.0914517327700801, 0.06552802993598945, 0.042015287687407414, 0.024106415033917344, 0.012376646156917807, 0.005686150859443048, 0.002337646503995043, 0.0008599720895460722],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003138196197111826, 0.0007632554149722213, 0.001638142852500863, 0.003090213329823024, 0.005092926974060729, 0.007262597661114692, 0.008809825084618847, 0.008782215250663696, 0.006580595749872409, 0.00245131374472136] + [0.0] * 32 + [-0.00245131374472136, -0.006580595749872409, -0.008782215250663696, -0.008809825084618847, -0.007262597661114692, -0.005092926974060729, -0.003090213329823024, -0.001638142852500863, -0.0007632554149722213, -0.0003138196197111826],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008599720895460722, -0.002337646503995043, -0.005686150859443048, -0.012376646156917807, -0.024106415033917344, -0.042015287687407414, -0.06552802993598945, -0.0914517327700801, -0.11420939303815864, -0.1276311745495765] + [-0.1294161970468906] * 32 + [-0.1276311745495765, -0.11420939303815864, -0.0914517327700801, -0.06552802993598945, -0.042015287687407414, -0.024106415033917344, -0.012376646156917807, -0.005686150859443048, -0.002337646503995043, -0.0008599720895460722],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0003138196197111826, -0.0007632554149722213, -0.001638142852500863, -0.003090213329823024, -0.005092926974060729, -0.007262597661114692, -0.008809825084618847, -0.008782215250663696, -0.006580595749872409, -0.00245131374472136] + [0.0] * 32 + [0.00245131374472136, 0.006580595749872409, 0.008782215250663696, 0.008809825084618847, 0.007262597661114692, 0.005092926974060729, 0.003090213329823024, 0.001638142852500863, 0.0007632554149722213, 0.0003138196197111826],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006284517393142791, -0.0015284869490371185, -0.00328052696592678, -0.006188427427726713, -0.010199039875182862, -0.014543998671172639, -0.017642459393006495, -0.017587168241397614, -0.013178229100327028, -0.004908974103954795] + [0.0] * 32 + [0.004908974103954795, 0.013178229100327028, 0.017587168241397614, 0.017642459393006495, 0.014543998671172639, 0.010199039875182862, 0.006188427427726713, 0.00328052696592678, 0.0015284869490371185, 0.0006284517393142791],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0017221707040954192, 0.004681345330447098, 0.011387023542088086, 0.024785336274866496, 0.04827524318154477, 0.08413935575233286, 0.13122571630483457, 0.18314024016584937, 0.22871448179981746, 0.25559279470870994] + [0.25916746124544393] * 32 + [0.25559279470870994, 0.22871448179981746, 0.18314024016584937, 0.13122571630483457, 0.08413935575233286, 0.04827524318154477, 0.024785336274866496, 0.011387023542088086, 0.004681345330447098, 0.0017221707040954192],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003127532136030457, -0.000760661758663084, -0.0016325761975367295, -0.0030797123217171495, -0.005075620444792635, -0.007237918265626666, -0.008779887978422295, -0.008752371966821531, -0.0065582338991082584, -0.0024429838131742607] + [0.0] * 32 + [0.0024429838131742607, 0.0065582338991082584, 0.008752371966821531, 0.008779887978422295, 0.007237918265626666, 0.005075620444792635, 0.0030797123217171495, 0.0016325761975367295, 0.000760661758663084, 0.0003127532136030457],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008570497754792741, 0.0023297028307702155, 0.005666828466490438, 0.01233458845806477, 0.024024497822172863, 0.04187251344191499, 0.0653053558678664, 0.09114096607386311, 0.11382129240106464, 0.1271974646870331] + [0.1289764214103333] * 32 + [0.1271974646870331, 0.11382129240106464, 0.09114096607386311, 0.0653053558678664, 0.04187251344191499, 0.024024497822172863, 0.01233458845806477, 0.005666828466490438, 0.0023297028307702155, 0.0008570497754792741],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0008400127900512386, -0.002043034502567416, -0.004384878642381167, -0.008271690353290131, -0.013632429358448805, -0.019440068565334388, -0.0235815904563419, -0.02350768617440165, -0.017614528375048785, -0.006561523782003884] + [0.0] * 32 + [0.006561523782003884, 0.017614528375048785, 0.02350768617440165, 0.0235815904563419, 0.019440068565334388, 0.013632429358448805, 0.008271690353290131, 0.004384878642381167, 0.002043034502567416, 0.0008400127900512386],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0023019196663695667, 0.006257266399664901, 0.015220334064800986, 0.03312903469616625, 0.06452654862500447, 0.11246390224927966, 0.1754013445805286, 0.24479229587339238, 0.30570858184181127, 0.3416351696862567] + [0.34641320660330166] * 32 + [0.3416351696862567, 0.30570858184181127, 0.24479229587339238, 0.1754013445805286, 0.11246390224927966, 0.06452654862500447, 0.03312903469616625, 0.015220334064800986, 0.006257266399664901, 0.0023019196663695667],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0023019196663695667, 0.006257266399664901, 0.015220334064800986, 0.03312903469616625, 0.06452654862500447, 0.11246390224927966, 0.1754013445805286, 0.24479229587339238, 0.30570858184181127, 0.3416351696862567] + [0.34641320660330166] * 32 + [0.3416351696862567, 0.30570858184181127, 0.24479229587339238, 0.1754013445805286, 0.11246390224927966, 0.06452654862500447, 0.03312903469616625, 0.015220334064800986, 0.006257266399664901, 0.0023019196663695667],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008400127900512386, 0.002043034502567416, 0.004384878642381167, 0.008271690353290131, 0.013632429358448805, 0.019440068565334388, 0.0235815904563419, 0.02350768617440165, 0.017614528375048785, 0.006561523782003884] + [0.0] * 32 + [-0.006561523782003884, -0.017614528375048785, -0.02350768617440165, -0.0235815904563419, -0.019440068565334388, -0.013632429358448805, -0.008271690353290131, -0.004384878642381167, -0.002043034502567416, -0.0008400127900512386],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003127532136030457, 0.000760661758663084, 0.0016325761975367295, 0.0030797123217171495, 0.005075620444792635, 0.007237918265626666, 0.008779887978422295, 0.008752371966821531, 0.0065582338991082584, 0.0024429838131742607] + [0.0] * 32 + [-0.0024429838131742607, -0.0065582338991082584, -0.008752371966821531, -0.008779887978422295, -0.007237918265626666, -0.005075620444792635, -0.0030797123217171495, -0.0016325761975367295, -0.000760661758663084, -0.0003127532136030457],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q2_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0008570497754792741, -0.0023297028307702155, -0.005666828466490438, -0.01233458845806477, -0.024024497822172863, -0.04187251344191499, -0.0653053558678664, -0.09114096607386311, -0.11382129240106464, -0.1271974646870331] + [-0.1289764214103333] * 32 + [-0.1271974646870331, -0.11382129240106464, -0.09114096607386311, -0.0653053558678664, -0.04187251344191499, -0.024024497822172863, -0.01233458845806477, -0.005666828466490438, -0.0023297028307702155, -0.0008570497754792741],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001311080999574648, 0.0035638876567816863, 0.00866889105257577, 0.01886896773982359, 0.03675173078641692, 0.06405492230300033, 0.09990156196113596, 0.1394238611584692, 0.17411933131960183, 0.19458167298623746] + [0.19730305093383702] * 32 + [0.19458167298623746, 0.17411933131960183, 0.1394238611584692, 0.09990156196113596, 0.06405492230300033, 0.03675173078641692, 0.01886896773982359, 0.00866889105257577, 0.0035638876567816863, 0.001311080999574648],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.001063587408694751, 0.0028911303260327854, 0.0070324589967038255, 0.01530706074579276, 0.029814083283072335, 0.05196323404007412, 0.08104308082054011, 0.11310473056040195, 0.14125071483909798, 0.15785036730611132] + [0.16005802901450727] * 32 + [0.15785036730611132, 0.14125071483909798, 0.11310473056040195, 0.08104308082054011, 0.05196323404007412, 0.029814083283072335, 0.01530706074579276, 0.0070324589967038255, 0.0028911303260327854, 0.001063587408694751],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001063587408694751, 0.0028911303260327854, 0.0070324589967038255, 0.01530706074579276, 0.029814083283072335, 0.05196323404007412, 0.08104308082054011, 0.11310473056040195, 0.14125071483909798, 0.15785036730611132] + [0.16005802901450727] * 32 + [0.15785036730611132, 0.14125071483909798, 0.11310473056040195, 0.08104308082054011, 0.05196323404007412, 0.029814083283072335, 0.01530706074579276, 0.0070324589967038255, 0.0028911303260327854, 0.001063587408694751],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006509372807104426, 0.0017694309816217407, 0.004304008959301125, 0.009368234727189726, 0.018246829682737997, 0.031802563650576134, 0.04960002555357382, 0.06922241194715517, 0.08644833086977327, 0.09660765820787753] + [0.09795879239529275] * 32 + [0.09660765820787753, 0.08644833086977327, 0.06922241194715517, 0.04960002555357382, 0.031802563650576134, 0.018246829682737997, 0.009368234727189726, 0.004304008959301125, 0.0017694309816217407, 0.0006509372807104426],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006509372807104426, -0.0017694309816217407, -0.004304008959301125, -0.009368234727189726, -0.018246829682737997, -0.031802563650576134, -0.04960002555357382, -0.06922241194715517, -0.08644833086977327, -0.09660765820787753] + [-0.09795879239529275] * 32 + [-0.09660765820787753, -0.08644833086977327, -0.06922241194715517, -0.04960002555357382, -0.031802563650576134, -0.018246829682737997, -0.009368234727189726, -0.004304008959301125, -0.0017694309816217407, -0.0006509372807104426],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001309908128409933, 0.003560699462407518, 0.008661136007426828, 0.01885208787643059, 0.036718853301878025, 0.06399761983934506, 0.09981219169234844, 0.13929913490091606, 0.17396356707392177, 0.1944076034714618] + [0.19712654691980153] * 32 + [0.1944076034714618, 0.17396356707392177, 0.13929913490091606, 0.09981219169234844, 0.06399761983934506, 0.036718853301878025, 0.01885208787643059, 0.008661136007426828, 0.003560699462407518, 0.001309908128409933],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000650507994801753, 0.001768264061536936, 0.004301170513183727, 0.009362056480411034, 0.018234796101173102, 0.03178159021298089, 0.049567314887474685, 0.06917676053511437, 0.08639131915547779, 0.09654394653001067] + [0.09789418965943214] * 32 + [0.09654394653001067, 0.08639131915547779, 0.06917676053511437, 0.049567314887474685, 0.03178159021298089, 0.018234796101173102, 0.009362056480411034, 0.004301170513183727, 0.001768264061536936, 0.000650507994801753],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000650507994801753, -0.001768264061536936, -0.004301170513183727, -0.009362056480411034, -0.018234796101173102, -0.03178159021298089, -0.049567314887474685, -0.06917676053511437, -0.08639131915547779, -0.09654394653001067] + [-0.09789418965943214] * 32 + [-0.09654394653001067, -0.08639131915547779, -0.06917676053511437, -0.049567314887474685, -0.03178159021298089, -0.018234796101173102, -0.009362056480411034, -0.004301170513183727, -0.001768264061536936, -0.000650507994801753],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_ro_wf": {
            "type": "arbitrary",
            "samples": [0.000311223896625865, 0.00032577165523137104, 0.0003409211562887489, 0.0003566932662804085, 0.00037310938088465655, 0.0003901914293614473, 0.0004079618785141323, 0.0004264437362021095, 0.0004456605543788675, 0.0004656364316295382, 0.0004863960151817112, 0.0005079645023629436, 0.0005303676414781189, 0.0005536317320795551, 0.0005777836246025627, 0.0006028507193389735, 0.0006288609647210594, 0.0006558428548881647, 0.0006838254265083703, 0.0007128382548275099, 0.000742911448917959, 0.0007740756460997302, 0.0008063620055066135, 0.0008398022007703349, 0.0008744284117960341, 0.0009102733156027127, 0.0009473700762027662, 0.0009857523334951988, 0.0010254541911477047, 0.0010665102034434334, 0.001108955361068983, 0.0011528250758209412, 0.001198155164209159, 0.0012449818299358857, 0.0012933416452308927, 0.001343271531023825, 0.001394808735936162, 0.001447990814076442, 0.0015028556016237094, 0.0015594411921855662, 0.0016177859109186856, 0.001677928287401205, 0.0017399070272480768, 0.0018037609824621485, 0.0018695291205155869, 0.0019372504921580757, 0.0020069641979502434, 0.0020787093535227347, 0.002152525053563493, 0.0022284503345379554, 0.0023065241361491322, 0.0023867852615468304, 0.002469272336297659, 0.0025540237661298947, 0.0026410776934697776, 0.0027304719527883443, 0.0028222440247805333, 0.0029164309894009134, 0.0030130694777831214, 0.0031121956230727955, 0.003213845010206586, 0.003318052624672616, 0.0034248528002906085, 0.003534279166052743, 0.0036463645920691633, 0.0037611411346649593, 0.0038786399806783195, 0.003998891391012432, 0.00412192464349661, 0.004247767975114953, 0.0043764485236637415, 0.004507992268901533, 0.0046424239732587745, 0.00477976712217646, 0.004920043864146036, 0.0050632749505254955, 0.005209479675209109, 0.005358675814230768, 0.005510879565383436, 0.005666105487939465, 0.005824366442558891, 0.005985673531474939, 0.006150036039048107, 0.0063174613727820786, 0.006487955004896619, 0.006661520414554313, 0.006838159030839568, 0.0070178701765897375, 0.007200651013179588, 0.007386496486361374, 0.007575399273263843, 0.0077673497306542764, 0.007962335844568335, 0.008160343181412896, 0.008361354840647449, 0.008565351409149572, 0.00877231091737005, 0.008982208797382775, 0.009195017842934177, 0.009410708171596123, 0.009629247189125369, 0.009850599556131497, 0.010074727157153912, 0.010301589072246911, 0.010531141551170058, 0.010763337990279074, 0.010998128912210215, 0.011235461948448692, 0.011475281824868948, 0.011717530350331776, 0.011962146408420072, 0.01220906595239174, 0.01245822200342467, 0.012709544652224925, 0.01296296106406537, 0.013218395487317664, 0.013475769265536262, 0.013735000853148428, 0.013996005834799456, 0.014258696948397421, 0.01452298411189651, 0.014788774453852823, 0.015055972347780855, 0.015324479450333491, 0.01559419474332229, 0.015865014579589134, 0.01613683273273416, 0.016409540450698784, 0.01668302651319626, 0.016957177292976036, 0.017231876820901517, 0.017507006854814478, 0.017782446952152715, 0.018058074546280917, 0.018333765026488123, 0.01860939182159837, 0.018884826487134514, 0.019159938795968574, 0.01943459683238516, 0.019708667089478053, 0.019982014569793396, 0.02025450288912642, 0.020525994383372263, 0.02079635021832506, 0.021065430502313257, 0.021333094401553034, 0.021599200258095815, 0.02186360571023976, 0.022126167815269906, 0.02238674317438578, 0.02264518805967022, 0.022901358542948013, 0.02315511062637814, 0.023406300374618723, 0.0236547840483995, 0.02390041823933236, 0.02414306000578686, 0.02438256700965382, 0.02461879765381692, 0.024851611220149287, 0.02508086800784923, 0.025306429471927034, 0.025528158361652602, 0.025745918858772126, 0.025959576715300386, 0.026168999390694562, 0.026374056188214413, 0.026574618390273603, 0.026770559392586914, 0.026961754836918376, 0.027148082742236273, 0.02732942363408195, 0.027505660671960867, 0.027676679774566282, 0.027842369742647952, 0.028002622379341046, 0.028157332607773172, 0.02830639858577082, 0.02844972181749017, 0.02858720726180099, 0.028718763437256954, 0.028844302523490076, 0.028963740458872005, 0.029076997034290324, 0.029183995982893302, 0.029284665065662692, 0.02937893615268013, 0.02946674529995916, 0.029548032821721682, 0.029622743358004387, 0.029690825937488025, 0.0297522340354497, 0.029806925626745914, 0.029854863233741962, 0.02989601396911107, 0.02993034957343494, 0.029957846447545455, 0.0299784856795558, 0.029992253066537564, 0.029999139130809132] + [0.03] * 3200 + [0.029999139130809132, 0.029992253066537564, 0.0299784856795558, 0.029957846447545455, 0.02993034957343494, 0.02989601396911107, 0.029854863233741962, 0.029806925626745914, 0.0297522340354497, 0.029690825937488025, 0.029622743358004387, 0.029548032821721682, 0.02946674529995916, 0.02937893615268013, 0.029284665065662692, 0.029183995982893302, 0.029076997034290324, 0.028963740458872005, 0.028844302523490076, 0.028718763437256954, 0.02858720726180099, 0.02844972181749017, 0.02830639858577082, 0.028157332607773172, 0.028002622379341046, 0.027842369742647952, 0.027676679774566282, 0.027505660671960867, 0.02732942363408195, 0.027148082742236273, 0.026961754836918376, 0.026770559392586914, 0.026574618390273603, 0.026374056188214413, 0.026168999390694562, 0.025959576715300386, 0.025745918858772126, 0.025528158361652602, 0.025306429471927034, 0.02508086800784923, 0.024851611220149287, 0.02461879765381692, 0.02438256700965382, 0.02414306000578686, 0.02390041823933236, 0.0236547840483995, 0.023406300374618723, 0.02315511062637814, 0.022901358542948013, 0.02264518805967022, 0.02238674317438578, 0.022126167815269906, 0.02186360571023976, 0.021599200258095815, 0.021333094401553034, 0.021065430502313257, 0.02079635021832506, 0.020525994383372263, 0.02025450288912642, 0.019982014569793396, 0.019708667089478053, 0.01943459683238516, 0.019159938795968574, 0.018884826487134514, 0.01860939182159837, 0.018333765026488123, 0.018058074546280917, 0.017782446952152715, 0.017507006854814478, 0.017231876820901517, 0.016957177292976036, 0.01668302651319626, 0.016409540450698784, 0.01613683273273416, 0.015865014579589134, 0.01559419474332229, 0.015324479450333491, 0.015055972347780855, 0.014788774453852823, 0.01452298411189651, 0.014258696948397421, 0.013996005834799456, 0.013735000853148428, 0.013475769265536262, 0.013218395487317664, 0.01296296106406537, 0.012709544652224925, 0.01245822200342467, 0.01220906595239174, 0.011962146408420072, 0.011717530350331776, 0.011475281824868948, 0.011235461948448692, 0.010998128912210215, 0.010763337990279074, 0.010531141551170058, 0.010301589072246911, 0.010074727157153912, 0.009850599556131497, 0.009629247189125369, 0.009410708171596123, 0.009195017842934177, 0.008982208797382775, 0.00877231091737005, 0.008565351409149572, 0.008361354840647449, 0.008160343181412896, 0.007962335844568335, 0.0077673497306542764, 0.007575399273263843, 0.007386496486361374, 0.007200651013179588, 0.0070178701765897375, 0.006838159030839568, 0.006661520414554313, 0.006487955004896619, 0.0063174613727820786, 0.006150036039048107, 0.005985673531474939, 0.005824366442558891, 0.005666105487939465, 0.005510879565383436, 0.005358675814230768, 0.005209479675209109, 0.0050632749505254955, 0.004920043864146036, 0.00477976712217646, 0.0046424239732587745, 0.004507992268901533, 0.0043764485236637415, 0.004247767975114953, 0.00412192464349661, 0.003998891391012432, 0.0038786399806783195, 0.0037611411346649593, 0.0036463645920691633, 0.003534279166052743, 0.0034248528002906085, 0.003318052624672616, 0.003213845010206586, 0.0031121956230727955, 0.0030130694777831214, 0.0029164309894009134, 0.0028222440247805333, 0.0027304719527883443, 0.0026410776934697776, 0.0025540237661298947, 0.002469272336297659, 0.0023867852615468304, 0.0023065241361491322, 0.0022284503345379554, 0.002152525053563493, 0.0020787093535227347, 0.0020069641979502434, 0.0019372504921580757, 0.0018695291205155869, 0.0018037609824621485, 0.0017399070272480768, 0.001677928287401205, 0.0016177859109186856, 0.0015594411921855662, 0.0015028556016237094, 0.001447990814076442, 0.001394808735936162, 0.001343271531023825, 0.0012933416452308927, 0.0012449818299358857, 0.001198155164209159, 0.0011528250758209412, 0.001108955361068983, 0.0010665102034434334, 0.0010254541911477047, 0.0009857523334951988, 0.0009473700762027662, 0.0009102733156027127, 0.0008744284117960341, 0.0008398022007703349, 0.0008063620055066135, 0.0007740756460997302, 0.000742911448917959, 0.0007128382548275099, 0.0006838254265083703, 0.0006558428548881647, 0.0006288609647210594, 0.0006028507193389735, 0.0005777836246025627, 0.0005536317320795551, 0.0005303676414781189, 0.0005079645023629436, 0.0004863960151817112, 0.0004656364316295382, 0.0004456605543788675, 0.0004264437362021095, 0.0004079618785141323, 0.0003901914293614473, 0.00037310938088465655, 0.0003566932662804085, 0.0003409211562887489, 0.00032577165523137104, 0.000311223896625865],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.001311080999574648, 0.0035638876567816863, 0.00866889105257577, 0.01886896773982359, 0.03675173078641692, 0.06405492230300033, 0.09990156196113596, 0.1394238611584692, 0.17411933131960183, 0.19458167298623746] + [0.19730305093383702] * 32 + [0.19458167298623746, 0.17411933131960183, 0.1394238611584692, 0.09990156196113596, 0.06405492230300033, 0.03675173078641692, 0.01886896773982359, 0.00866889105257577, 0.0035638876567816863, 0.001311080999574648],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0030801133862301787, -0.00749128822134264, -0.016078235430878638, -0.03033018602296031, -0.049986653359449684, -0.07128179014234601, -0.08646769822248304, -0.08619671000563695, -0.0645879982813234, -0.024059439897081876] + [0.0] * 32 + [0.024059439897081876, 0.0645879982813234, 0.08619671000563695, 0.08646769822248304, 0.07128179014234601, 0.049986653359449684, 0.03033018602296031, 0.016078235430878638, 0.00749128822134264, 0.0030801133862301787],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006509372807104426, 0.0017694309816217407, 0.004304008959301125, 0.009368234727189726, 0.018246829682737997, 0.031802563650576134, 0.04960002555357382, 0.06922241194715517, 0.08644833086977327, 0.09660765820787753] + [0.09795879239529275] * 32 + [0.09660765820787753, 0.08644833086977327, 0.06922241194715517, 0.04960002555357382, 0.031802563650576134, 0.018246829682737997, 0.009368234727189726, 0.004304008959301125, 0.0017694309816217407, 0.0006509372807104426],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0015292423828603817, -0.0037193421195189135, -0.007982666862988541, -0.01505860341171359, -0.02481782301793101, -0.03539062396181824, -0.04293026012008012, -0.04279571745411547, -0.03206723000441259, -0.011945247003887436] + [0.0] * 32 + [0.011945247003887436, 0.03206723000441259, 0.04279571745411547, 0.04293026012008012, 0.03539062396181824, 0.02481782301793101, 0.01505860341171359, 0.007982666862988541, 0.0037193421195189135, 0.0015292423828603817],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0006509372807104426, -0.0017694309816217407, -0.004304008959301125, -0.009368234727189726, -0.018246829682737997, -0.031802563650576134, -0.04960002555357382, -0.06922241194715517, -0.08644833086977327, -0.09660765820787753] + [-0.09795879239529275] * 32 + [-0.09660765820787753, -0.08644833086977327, -0.06922241194715517, -0.04960002555357382, -0.031802563650576134, -0.018246829682737997, -0.009368234727189726, -0.004304008959301125, -0.0017694309816217407, -0.0006509372807104426],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0015292423828603817, 0.0037193421195189135, 0.007982666862988541, 0.01505860341171359, 0.02481782301793101, 0.03539062396181824, 0.04293026012008012, 0.04279571745411547, 0.03206723000441259, 0.011945247003887436] + [0.0] * 32 + [-0.011945247003887436, -0.03206723000441259, -0.04279571745411547, -0.04293026012008012, -0.03539062396181824, -0.02481782301793101, -0.01505860341171359, -0.007982666862988541, -0.0037193421195189135, -0.0015292423828603817],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.003077357968238511, 0.007484586640018349, 0.016063852109998777, 0.030303053145114993, 0.04994193613422491, 0.07121802264342385, 0.08639034566382547, 0.08611959986851216, 0.06453021893680129, 0.024037916723987585] + [0.0] * 32 + [-0.024037916723987585, -0.06453021893680129, -0.08611959986851216, -0.08639034566382547, -0.07121802264342385, -0.04994193613422491, -0.030303053145114993, -0.016063852109998777, -0.007484586640018349, -0.003077357968238511],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001309908128409933, 0.003560699462407518, 0.008661136007426828, 0.01885208787643059, 0.036718853301878025, 0.06399761983934506, 0.09981219169234844, 0.13929913490091606, 0.17396356707392177, 0.1944076034714618] + [0.19712654691980153] * 32 + [0.1944076034714618, 0.17396356707392177, 0.13929913490091606, 0.09981219169234844, 0.06399761983934506, 0.036718853301878025, 0.01885208787643059, 0.008661136007426828, 0.003560699462407518, 0.001309908128409933],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0015282338644894316, 0.003716889254690273, 0.00797740238283109, 0.015048672429972708, 0.024801455939225173, 0.03536728423828917, 0.042901948090224, 0.042767494153653614, 0.032046082022295815, 0.011937369246127134] + [0.0] * 32 + [-0.011937369246127134, -0.032046082022295815, -0.042767494153653614, -0.042901948090224, -0.03536728423828917, -0.024801455939225173, -0.015048672429972708, -0.00797740238283109, -0.003716889254690273, -0.0015282338644894316],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.000650507994801753, 0.001768264061536936, 0.004301170513183727, 0.009362056480411034, 0.018234796101173102, 0.03178159021298089, 0.049567314887474685, 0.06917676053511437, 0.08639131915547779, 0.09654394653001067] + [0.09789418965943214] * 32 + [0.09654394653001067, 0.08639131915547779, 0.06917676053511437, 0.049567314887474685, 0.03178159021298089, 0.018234796101173102, 0.009362056480411034, 0.004301170513183727, 0.001768264061536936, 0.000650507994801753],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0024986784310118055, 0.006077152997952269, 0.01304313674277964, 0.024604737592761845, 0.04055064113746455, 0.0578258814590534, 0.07014513605039417, 0.06992530245091737, 0.05239568092825722, 0.019517724185680613] + [0.0] * 32 + [-0.019517724185680613, -0.05239568092825722, -0.06992530245091737, -0.07014513605039417, -0.0578258814590534, -0.04055064113746455, -0.024604737592761845, -0.01304313674277964, -0.006077152997952269, -0.0024986784310118055],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.001063587408694751, 0.0028911303260327854, 0.0070324589967038255, 0.01530706074579276, 0.029814083283072335, 0.05196323404007412, 0.08104308082054011, 0.11310473056040195, 0.14125071483909798, 0.15785036730611132] + [0.16005802901450727] * 32 + [0.15785036730611132, 0.14125071483909798, 0.11310473056040195, 0.08104308082054011, 0.05196323404007412, 0.029814083283072335, 0.01530706074579276, 0.0070324589967038255, 0.0028911303260327854, 0.001063587408694751],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.001063587408694751, 0.0028911303260327854, 0.0070324589967038255, 0.01530706074579276, 0.029814083283072335, 0.05196323404007412, 0.08104308082054011, 0.11310473056040195, 0.14125071483909798, 0.15785036730611132] + [0.16005802901450727] * 32 + [0.15785036730611132, 0.14125071483909798, 0.11310473056040195, 0.08104308082054011, 0.05196323404007412, 0.029814083283072335, 0.01530706074579276, 0.0070324589967038255, 0.0028911303260327854, 0.001063587408694751],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0024986784310118055, -0.006077152997952269, -0.01304313674277964, -0.024604737592761845, -0.04055064113746455, -0.0578258814590534, -0.07014513605039417, -0.06992530245091737, -0.05239568092825722, -0.019517724185680613] + [0.0] * 32 + [0.019517724185680613, 0.05239568092825722, 0.06992530245091737, 0.07014513605039417, 0.0578258814590534, 0.04055064113746455, 0.024604737592761845, 0.01304313674277964, 0.006077152997952269, 0.0024986784310118055],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0015282338644894316, -0.003716889254690273, -0.00797740238283109, -0.015048672429972708, -0.024801455939225173, -0.03536728423828917, -0.042901948090224, -0.042767494153653614, -0.032046082022295815, -0.011937369246127134] + [0.0] * 32 + [0.011937369246127134, 0.032046082022295815, 0.042767494153653614, 0.042901948090224, 0.03536728423828917, 0.024801455939225173, 0.015048672429972708, 0.00797740238283109, 0.003716889254690273, 0.0015282338644894316],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q3_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.000650507994801753, -0.001768264061536936, -0.004301170513183727, -0.009362056480411034, -0.018234796101173102, -0.03178159021298089, -0.049567314887474685, -0.06917676053511437, -0.08639131915547779, -0.09654394653001067] + [-0.09789418965943214] * 32 + [-0.09654394653001067, -0.08639131915547779, -0.06917676053511437, -0.049567314887474685, -0.03178159021298089, -0.018234796101173102, -0.009362056480411034, -0.004301170513183727, -0.001768264061536936, -0.000650507994801753],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007285172954878752, 0.0019803153260428198, 0.0048169694065816285, 0.010484759790527026, 0.02042152355629078, 0.035592857172064334, 0.055511456392513564, 0.07747247827601657, 0.0967514168737607, 0.10812155328422088] + [0.10963371836252556] * 32 + [0.10812155328422088, 0.0967514168737607, 0.07747247827601657, 0.055511456392513564, 0.035592857172064334, 0.02042152355629078, 0.010484759790527026, 0.0048169694065816285, 0.0019803153260428198, 0.0007285172954878752],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003639874941886334, 0.0009894205912393044, 0.002406691831126384, 0.005238477476046673, 0.010203160903394286, 0.01778318095303098, 0.027735066876540457, 0.03870740394349351, 0.04833969763682312, 0.054020533886365844] + [0.05477605359888424] * 32 + [0.054020533886365844, 0.04833969763682312, 0.03870740394349351, 0.027735066876540457, 0.01778318095303098, 0.010203160903394286, 0.005238477476046673, 0.002406691831126384, 0.0009894205912393044, 0.0003639874941886334],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003639874941886334, -0.0009894205912393044, -0.002406691831126384, -0.005238477476046673, -0.010203160903394286, -0.01778318095303098, -0.027735066876540457, -0.03870740394349351, -0.04833969763682312, -0.054020533886365844] + [-0.05477605359888424] * 32 + [-0.054020533886365844, -0.04833969763682312, -0.03870740394349351, -0.027735066876540457, -0.01778318095303098, -0.010203160903394286, -0.005238477476046673, -0.002406691831126384, -0.0009894205912393044, -0.0003639874941886334],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0007303611396639445, 0.0019853274141611392, 0.0048291609372997585, 0.010511296241201545, 0.02047320950459831, 0.035682941076472435, 0.0556519533665846, 0.0776685575987171, 0.09699629031414987, 0.1083952040232842] + [0.1099111963226997] * 32 + [0.1083952040232842, 0.09699629031414987, 0.0776685575987171, 0.0556519533665846, 0.035682941076472435, 0.02047320950459831, 0.010511296241201545, 0.0048291609372997585, 0.0019853274141611392, 0.0007303611396639445],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00036409595561075507, 0.0009897154199521466, 0.002407408979992156, 0.005240038443733408, 0.010206201253294727, 0.017788480006231455, 0.027743331404426988, 0.038718938021299415, 0.04835410195684601, 0.05403663098866368] + [0.05479237583183565] * 32 + [0.05403663098866368, 0.04835410195684601, 0.038718938021299415, 0.027743331404426988, 0.017788480006231455, 0.010206201253294727, 0.005240038443733408, 0.002407408979992156, 0.0009897154199521466, 0.00036409595561075507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00036409595561075507, -0.0009897154199521466, -0.002407408979992156, -0.005240038443733408, -0.010206201253294727, -0.017788480006231455, -0.027743331404426988, -0.038718938021299415, -0.04835410195684601, -0.05403663098866368] + [-0.05479237583183565] * 32 + [-0.05403663098866368, -0.04835410195684601, -0.038718938021299415, -0.027743331404426988, -0.017788480006231455, -0.010206201253294727, -0.005240038443733408, -0.002407408979992156, -0.0009897154199521466, -0.00036409595561075507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0002074825977505767, 0.00021718110348758075, 0.000227280770859166, 0.00023779551085360574, 0.00024873958725643775, 0.00026012761957429825, 0.00027197458567608827, 0.00028429582413473973, 0.00029710703625257837, 0.0003104242877530255, 0.00032426401012114085, 0.00033864300157529585, 0.00035357842765207934, 0.0003690878213863702, 0.00038518908306837523, 0.00040190047955931577, 0.00041924064314737306, 0.0004372285699254432, 0.000455883617672247, 0.0004752255032183401, 0.0004952742992786395, 0.0005160504307331536, 0.0005375746703377424, 0.00055986813384689, 0.0005829522745306895, 0.0006068488770684752, 0.0006315800508018443, 0.0006571682223301327, 0.0006836361274318032, 0.0007110068022956224, 0.0007393035740459889, 0.0007685500505472943, 0.0007987701094727728, 0.0008299878866239239, 0.000862227763487262, 0.0008955143540158835, 0.0009298724906241083, 0.0009653272093842949, 0.0010019037344158065, 0.0010396274614570445, 0.0010785239406124573, 0.0011186188582674702, 0.0011599380181653847, 0.0012025073216414327, 0.0012463527470103915, 0.0012915003281053841, 0.0013379761319668292, 0.0013858062356818235, 0.001435016702375662, 0.0014856335563586374, 0.001537682757432755, 0.001591190174364554, 0.0016461815575317732, 0.0017026825107532635, 0.0017607184623131857, 0.0018203146351922297, 0.001881496016520356, 0.0019442873262672763, 0.002008712985188748, 0.002074797082048531, 0.0021425633401377245, 0.0022120350831150775, 0.0022832352001937394, 0.0023561861107018293, 0.0024309097280461093, 0.0025074274231099737, 0.00258575998711888, 0.002665927594008288, 0.002747949762331074, 0.002831845316743303, 0.0029176323491091616, 0.003005328179267689, 0.0030949493155058507, 0.003186511414784307, 0.0032800292427640244, 0.0033755166336836644, 0.0034729864501394066, 0.003572450542820513, 0.003673919710255625, 0.003777403658626311, 0.003882910961705928, 0.003990449020983293, 0.004100024026032072, 0.004211640915188053, 0.004325303336597747, 0.0044410136097028765, 0.00455877268722638, 0.0046785801177264925, 0.004800434008786394, 0.004924330990907584, 0.005050266182175896, 0.005178233153769519, 0.00530822389637889, 0.005440228787608598, 0.005574236560431633, 0.005710234272766382, 0.005848207278246701, 0.005988139198255185, 0.006130011895289452, 0.00627380544773075, 0.00641949812608358, 0.0065670663707543325, 0.006716484771435942, 0.006867726048164609, 0.007020761034113373, 0.00717555866018605, 0.007332085941473478, 0.007490307965632463, 0.007650187883245967, 0.007811686900221186, 0.00797476427228005, 0.008139377301594496, 0.008305481335616448, 0.008473029768149952, 0.008641974042710249, 0.008812263658211777, 0.008983846177024177, 0.009156667235432287, 0.009330670556532972, 0.009505797965598282, 0.009681989407931009, 0.009859182969235217, 0.010037314898520572, 0.010216319633555664, 0.010396129828881528, 0.010576676386392758, 0.010757888488489442, 0.010939693633799192, 0.011122017675464176, 0.011304784861984028, 0.011487917880601016, 0.011671337903209655, 0.011854964634768478, 0.01203871636418728, 0.012222510017658752, 0.012406261214398915, 0.012589884324756344, 0.012773292530645719, 0.012956397888256777, 0.013139111392985372, 0.013321343046528933, 0.013503001926084283, 0.013683996255581513, 0.013864233478883378, 0.014043620334875507, 0.014222062934368694, 0.014399466838730546, 0.014575737140159844, 0.014750778543513275, 0.014924495449590524, 0.01509679203978015, 0.015267572361965345, 0.015436740417585429, 0.01560420024974582, 0.015769856032266338, 0.01593361215955491, 0.016095373337191243, 0.016255044673102553, 0.016412531769211283, 0.01656774081343286, 0.01672057867189949, 0.016870952981284694, 0.01701877224110174, 0.017163945905848087, 0.01730638447686693, 0.017445999593796377, 0.01758270412547628, 0.017716412260182408, 0.017847039595057946, 0.017974503224612255, 0.01809872182815752, 0.018219615756054637, 0.018337107114640584, 0.01845111984971086, 0.018561579828431974, 0.018668414919560703, 0.018771555071848786, 0.018870932390513885, 0.018966481211660117, 0.019058138174533997, 0.019145842291504643, 0.019229535015660056, 0.019309160305914674, 0.019384664689526886, 0.01945599732192887, 0.019523110043775133, 0.01958595743512009, 0.019644496866639445, 0.01969868854781446, 0.01974849557200293, 0.019793883958325355, 0.019834822690299805, 0.019871283751163947, 0.01990324215582798, 0.019930675979407387, 0.019953566382289963, 0.019971897631696975, 0.019985657119703872, 0.019994835377691714, 0.019999426087206094] + [0.020000000000000004] * 3200 + [0.019999426087206094, 0.019994835377691714, 0.019985657119703872, 0.019971897631696975, 0.019953566382289963, 0.019930675979407387, 0.01990324215582798, 0.019871283751163947, 0.019834822690299805, 0.019793883958325355, 0.01974849557200293, 0.01969868854781446, 0.019644496866639445, 0.01958595743512009, 0.019523110043775133, 0.01945599732192887, 0.019384664689526886, 0.019309160305914674, 0.019229535015660056, 0.019145842291504643, 0.019058138174533997, 0.018966481211660117, 0.018870932390513885, 0.018771555071848786, 0.018668414919560703, 0.018561579828431974, 0.01845111984971086, 0.018337107114640584, 0.018219615756054637, 0.01809872182815752, 0.017974503224612255, 0.017847039595057946, 0.017716412260182408, 0.01758270412547628, 0.017445999593796377, 0.01730638447686693, 0.017163945905848087, 0.01701877224110174, 0.016870952981284694, 0.01672057867189949, 0.01656774081343286, 0.016412531769211283, 0.016255044673102553, 0.016095373337191243, 0.01593361215955491, 0.015769856032266338, 0.01560420024974582, 0.015436740417585429, 0.015267572361965345, 0.01509679203978015, 0.014924495449590524, 0.014750778543513275, 0.014575737140159844, 0.014399466838730546, 0.014222062934368694, 0.014043620334875507, 0.013864233478883378, 0.013683996255581513, 0.013503001926084283, 0.013321343046528933, 0.013139111392985372, 0.012956397888256777, 0.012773292530645719, 0.012589884324756344, 0.012406261214398915, 0.012222510017658752, 0.01203871636418728, 0.011854964634768478, 0.011671337903209655, 0.011487917880601016, 0.011304784861984028, 0.011122017675464176, 0.010939693633799192, 0.010757888488489442, 0.010576676386392758, 0.010396129828881528, 0.010216319633555664, 0.010037314898520572, 0.009859182969235217, 0.009681989407931009, 0.009505797965598282, 0.009330670556532972, 0.009156667235432287, 0.008983846177024177, 0.008812263658211777, 0.008641974042710249, 0.008473029768149952, 0.008305481335616448, 0.008139377301594496, 0.00797476427228005, 0.007811686900221186, 0.007650187883245967, 0.007490307965632463, 0.007332085941473478, 0.00717555866018605, 0.007020761034113373, 0.006867726048164609, 0.006716484771435942, 0.0065670663707543325, 0.00641949812608358, 0.00627380544773075, 0.006130011895289452, 0.005988139198255185, 0.005848207278246701, 0.005710234272766382, 0.005574236560431633, 0.005440228787608598, 0.00530822389637889, 0.005178233153769519, 0.005050266182175896, 0.004924330990907584, 0.004800434008786394, 0.0046785801177264925, 0.00455877268722638, 0.0044410136097028765, 0.004325303336597747, 0.004211640915188053, 0.004100024026032072, 0.003990449020983293, 0.003882910961705928, 0.003777403658626311, 0.003673919710255625, 0.003572450542820513, 0.0034729864501394066, 0.0033755166336836644, 0.0032800292427640244, 0.003186511414784307, 0.0030949493155058507, 0.003005328179267689, 0.0029176323491091616, 0.002831845316743303, 0.002747949762331074, 0.002665927594008288, 0.00258575998711888, 0.0025074274231099737, 0.0024309097280461093, 0.0023561861107018293, 0.0022832352001937394, 0.0022120350831150775, 0.0021425633401377245, 0.002074797082048531, 0.002008712985188748, 0.0019442873262672763, 0.001881496016520356, 0.0018203146351922297, 0.0017607184623131857, 0.0017026825107532635, 0.0016461815575317732, 0.001591190174364554, 0.001537682757432755, 0.0014856335563586374, 0.001435016702375662, 0.0013858062356818235, 0.0013379761319668292, 0.0012915003281053841, 0.0012463527470103915, 0.0012025073216414327, 0.0011599380181653847, 0.0011186188582674702, 0.0010785239406124573, 0.0010396274614570445, 0.0010019037344158065, 0.0009653272093842949, 0.0009298724906241083, 0.0008955143540158835, 0.000862227763487262, 0.0008299878866239239, 0.0007987701094727728, 0.0007685500505472943, 0.0007393035740459889, 0.0007110068022956224, 0.0006836361274318032, 0.0006571682223301327, 0.0006315800508018443, 0.0006068488770684752, 0.0005829522745306895, 0.00055986813384689, 0.0005375746703377424, 0.0005160504307331536, 0.0004952742992786395, 0.0004752255032183401, 0.000455883617672247, 0.0004372285699254432, 0.00041924064314737306, 0.00040190047955931577, 0.00038518908306837523, 0.0003690878213863702, 0.00035357842765207934, 0.00033864300157529585, 0.00032426401012114085, 0.0003104242877530255, 0.00029710703625257837, 0.00028429582413473973, 0.00027197458567608827, 0.00026012761957429825, 0.00024873958725643775, 0.00023779551085360574, 0.000227280770859166, 0.00021718110348758075, 0.0002074825977505767],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0007285172954878752, 0.0019803153260428198, 0.0048169694065816285, 0.010484759790527026, 0.02042152355629078, 0.035592857172064334, 0.055511456392513564, 0.07747247827601657, 0.0967514168737607, 0.10812155328422088] + [0.10963371836252556] * 32 + [0.10812155328422088, 0.0967514168737607, 0.07747247827601657, 0.055511456392513564, 0.035592857172064334, 0.02042152355629078, 0.010484759790527026, 0.0048169694065816285, 0.0019803153260428198, 0.0007285172954878752],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002884749000429387, -0.0007016133336213376, -0.0015058430574422168, -0.002840641328456392, -0.004681611688651863, -0.006676055296575471, -0.008098325442558795, -0.008072945435732759, -0.006049133266156289, -0.002253340591430135] + [0.0] * 32 + [0.002253340591430135, 0.006049133266156289, 0.008072945435732759, 0.008098325442558795, 0.006676055296575471, 0.004681611688651863, 0.002840641328456392, 0.0015058430574422168, 0.0007016133336213376, 0.0002884749000429387],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003639874941886334, 0.0009894205912393044, 0.002406691831126384, 0.005238477476046673, 0.010203160903394286, 0.01778318095303098, 0.027735066876540457, 0.03870740394349351, 0.04833969763682312, 0.054020533886365844] + [0.05477605359888424] * 32 + [0.054020533886365844, 0.04833969763682312, 0.03870740394349351, 0.027735066876540457, 0.01778318095303098, 0.010203160903394286, 0.005238477476046673, 0.002406691831126384, 0.0009894205912393044, 0.0003639874941886334],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00014413007989416126, -0.00035054552688847535, -0.0007523610551382784, -0.001419263379795382, -0.0023390633521959653, -0.0033355428258404368, -0.0040461485310201405, -0.004033467974025384, -0.0030223151505096636, -0.0011258316041473284] + [0.0] * 32 + [0.0011258316041473284, 0.0030223151505096636, 0.004033467974025384, 0.0040461485310201405, 0.0033355428258404368, 0.0023390633521959653, 0.001419263379795382, 0.0007523610551382784, 0.00035054552688847535, 0.00014413007989416126],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003639874941886334, -0.0009894205912393044, -0.002406691831126384, -0.005238477476046673, -0.010203160903394286, -0.01778318095303098, -0.027735066876540457, -0.03870740394349351, -0.04833969763682312, -0.054020533886365844] + [-0.05477605359888424] * 32 + [-0.054020533886365844, -0.04833969763682312, -0.03870740394349351, -0.027735066876540457, -0.01778318095303098, -0.010203160903394286, -0.005238477476046673, -0.002406691831126384, -0.0009894205912393044, -0.0003639874941886334],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00014413007989416126, 0.00035054552688847535, 0.0007523610551382784, 0.001419263379795382, 0.0023390633521959653, 0.0033355428258404368, 0.0040461485310201405, 0.004033467974025384, 0.0030223151505096636, 0.0011258316041473284] + [0.0] * 32 + [-0.0011258316041473284, -0.0030223151505096636, -0.004033467974025384, -0.0040461485310201405, -0.0033355428258404368, -0.0023390633521959653, -0.001419263379795382, -0.0007523610551382784, -0.00035054552688847535, -0.00014413007989416126],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002892050169086339, 0.0007033890850922535, 0.001509654277805461, 0.0028478308625995295, 0.004693460635135636, 0.006692952089217112, 0.008118821936321756, 0.008093377693851534, 0.006064443347621959, 0.0022590436940907606] + [0.0] * 32 + [-0.0022590436940907606, -0.006064443347621959, -0.008093377693851534, -0.008118821936321756, -0.006692952089217112, -0.004693460635135636, -0.0028478308625995295, -0.001509654277805461, -0.0007033890850922535, -0.0002892050169086339],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0007303611396639445, 0.0019853274141611392, 0.0048291609372997585, 0.010511296241201545, 0.02047320950459831, 0.035682941076472435, 0.0556519533665846, 0.0776685575987171, 0.09699629031414987, 0.1083952040232842] + [0.1099111963226997] * 32 + [0.1083952040232842, 0.09699629031414987, 0.0776685575987171, 0.0556519533665846, 0.035682941076472435, 0.02047320950459831, 0.010511296241201545, 0.0048291609372997585, 0.0019853274141611392, 0.0007303611396639445],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0001441730279450845, 0.0003506499828573527, 0.0007525852445714104, 0.0014196862935685077, 0.0023397603490479518, 0.0033365367548193565, 0.004047354207123843, 0.004034669871561781, 0.0030232157435370562, 0.001126167080774424] + [0.0] * 32 + [-0.001126167080774424, -0.0030232157435370562, -0.004034669871561781, -0.004047354207123843, -0.0033365367548193565, -0.0023397603490479518, -0.0014196862935685077, -0.0007525852445714104, -0.0003506499828573527, -0.0001441730279450845],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00036409595561075507, 0.0009897154199521466, 0.002407408979992156, 0.005240038443733408, 0.010206201253294727, 0.017788480006231455, 0.027743331404426988, 0.038718938021299415, 0.04835410195684601, 0.05403663098866368] + [0.05479237583183565] * 32 + [0.05403663098866368, 0.04835410195684601, 0.038718938021299415, 0.027743331404426988, 0.017788480006231455, 0.010206201253294727, 0.005240038443733408, 0.002407408979992156, 0.0009897154199521466, 0.00036409595561075507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002454983391833253, 0.0005970880243906021, 0.0012815048020392023, 0.0024174468151224146, 0.0039841521535988085, 0.005681466523990009, 0.006891848982418661, 0.006870250051200291, 0.005147942403720139, 0.0019176412669806935] + [0.0] * 32 + [-0.0019176412669806935, -0.005147942403720139, -0.006870250051200291, -0.006891848982418661, -0.005681466523990009, -0.0039841521535988085, -0.0024174468151224146, -0.0012815048020392023, -0.0005970880243906021, -0.0002454983391833253],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002454983391833253, -0.0005970880243906021, -0.0012815048020392023, -0.0024174468151224146, -0.0039841521535988085, -0.005681466523990009, -0.006891848982418661, -0.006870250051200291, -0.005147942403720139, -0.0019176412669806935] + [0.0] * 32 + [0.0019176412669806935, 0.005147942403720139, 0.006870250051200291, 0.006891848982418661, 0.005681466523990009, 0.0039841521535988085, 0.0024174468151224146, 0.0012815048020392023, 0.0005970880243906021, 0.0002454983391833253],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0001441730279450845, -0.0003506499828573527, -0.0007525852445714104, -0.0014196862935685077, -0.0023397603490479518, -0.0033365367548193565, -0.004047354207123843, -0.004034669871561781, -0.0030232157435370562, -0.001126167080774424] + [0.0] * 32 + [0.001126167080774424, 0.0030232157435370562, 0.004034669871561781, 0.004047354207123843, 0.0033365367548193565, 0.0023397603490479518, 0.0014196862935685077, 0.0007525852445714104, 0.0003506499828573527, 0.0001441730279450845],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q4_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00036409595561075507, -0.0009897154199521466, -0.002407408979992156, -0.005240038443733408, -0.010206201253294727, -0.017788480006231455, -0.027743331404426988, -0.038718938021299415, -0.04835410195684601, -0.05403663098866368] + [-0.05479237583183565] * 32 + [-0.05403663098866368, -0.04835410195684601, -0.038718938021299415, -0.027743331404426988, -0.017788480006231455, -0.010206201253294727, -0.005240038443733408, -0.002407408979992156, -0.0009897154199521466, -0.00036409595561075507],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008720809757939942, 0.0023705618694456468, 0.005766215032202263, 0.012550916231803613, 0.024445846791109577, 0.04260688635143973, 0.06645070111356702, 0.09273942412977619, 0.11581752493633832, 0.12942829261084438] + [0.13123844921964034] * 32 + [0.12942829261084438, 0.11581752493633832, 0.09273942412977619, 0.06645070111356702, 0.04260688635143973, 0.024445846791109577, 0.012550916231803613, 0.005766215032202263, 0.0023705618694456468, 0.0008720809757939942],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00023390439715249725, 0.0006358180723763009, 0.0015465800635439412, 0.0033663324581053593, 0.006556720322159072, 0.011427766851013911, 0.017823013706013142, 0.02487401938059161, 0.03106389097097776, 0.034714490509385854] + [0.0352] * 32 + [0.034714490509385854, 0.03106389097097776, 0.02487401938059161, 0.017823013706013142, 0.011427766851013911, 0.006556720322159072, 0.0033663324581053593, 0.0015465800635439412, 0.0006358180723763009, 0.00023390439715249725],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00023390439715249725, 0.0006358180723763009, 0.0015465800635439412, 0.0033663324581053593, 0.006556720322159072, 0.011427766851013911, 0.017823013706013142, 0.02487401938059161, 0.03106389097097776, 0.034714490509385854] + [0.0352] * 32 + [0.034714490509385854, 0.03106389097097776, 0.02487401938059161, 0.017823013706013142, 0.011427766851013911, 0.006556720322159072, 0.0033663324581053593, 0.0015465800635439412, 0.0006358180723763009, 0.00023390439715249725],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00043027546606994526, 0.0011696099806496787, 0.0028449890885206483, 0.006192488405480169, 0.012061320466190116, 0.02102178397592465, 0.032786068250465775, 0.04575664422007058, 0.05714313338354751, 0.06385854120377411] + [0.06475165319695818] * 32 + [0.06385854120377411, 0.05714313338354751, 0.04575664422007058, 0.032786068250465775, 0.02102178397592465, 0.012061320466190116, 0.006192488405480169, 0.0028449890885206483, 0.0011696099806496787, 0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00043027546606994526, -0.0011696099806496787, -0.0028449890885206483, -0.006192488405480169, -0.012061320466190116, -0.02102178397592465, -0.032786068250465775, -0.04575664422007058, -0.05714313338354751, -0.06385854120377411] + [-0.06475165319695818] * 32 + [-0.06385854120377411, -0.05714313338354751, -0.04575664422007058, -0.032786068250465775, -0.02102178397592465, -0.012061320466190116, -0.006192488405480169, -0.0028449890885206483, -0.0011696099806496787, -0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008677730473957577, 0.002358851705962418, 0.005737730932471792, 0.01248891688775228, 0.02432508855817774, 0.042396415740603745, 0.06612244620335157, 0.09228130749848398, 0.11524540649947819, 0.1287889393480744] + [0.13059015409794128] * 32 + [0.1287889393480744, 0.11524540649947819, 0.09228130749848398, 0.06612244620335157, 0.042396415740603745, 0.02432508855817774, 0.01248891688775228, 0.005737730932471792, 0.002358851705962418, 0.0008677730473957577],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00043027546606994526, 0.0011696099806496787, 0.0028449890885206483, 0.006192488405480169, 0.012061320466190116, 0.02102178397592465, 0.032786068250465775, 0.04575664422007058, 0.05714313338354751, 0.06385854120377411] + [0.06475165319695818] * 32 + [0.06385854120377411, 0.05714313338354751, 0.04575664422007058, 0.032786068250465775, 0.02102178397592465, 0.012061320466190116, 0.006192488405480169, 0.0028449890885206483, 0.0011696099806496787, 0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00043027546606994526, -0.0011696099806496787, -0.0028449890885206483, -0.006192488405480169, -0.012061320466190116, -0.02102178397592465, -0.032786068250465775, -0.04575664422007058, -0.05714313338354751, -0.06385854120377411] + [-0.06475165319695818] * 32 + [-0.06385854120377411, -0.05714313338354751, -0.04575664422007058, -0.032786068250465775, -0.02102178397592465, -0.012061320466190116, -0.006192488405480169, -0.0028449890885206483, -0.0011696099806496787, -0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_ro_wf": {
            "type": "arbitrary",
            "samples": [0.000311223896625865, 0.00032577165523137104, 0.0003409211562887489, 0.0003566932662804085, 0.00037310938088465655, 0.0003901914293614473, 0.0004079618785141323, 0.0004264437362021095, 0.0004456605543788675, 0.0004656364316295382, 0.0004863960151817112, 0.0005079645023629436, 0.0005303676414781189, 0.0005536317320795551, 0.0005777836246025627, 0.0006028507193389735, 0.0006288609647210594, 0.0006558428548881647, 0.0006838254265083703, 0.0007128382548275099, 0.000742911448917959, 0.0007740756460997302, 0.0008063620055066135, 0.0008398022007703349, 0.0008744284117960341, 0.0009102733156027127, 0.0009473700762027662, 0.0009857523334951988, 0.0010254541911477047, 0.0010665102034434334, 0.001108955361068983, 0.0011528250758209412, 0.001198155164209159, 0.0012449818299358857, 0.0012933416452308927, 0.001343271531023825, 0.001394808735936162, 0.001447990814076442, 0.0015028556016237094, 0.0015594411921855662, 0.0016177859109186856, 0.001677928287401205, 0.0017399070272480768, 0.0018037609824621485, 0.0018695291205155869, 0.0019372504921580757, 0.0020069641979502434, 0.0020787093535227347, 0.002152525053563493, 0.0022284503345379554, 0.0023065241361491322, 0.0023867852615468304, 0.002469272336297659, 0.0025540237661298947, 0.0026410776934697776, 0.0027304719527883443, 0.0028222440247805333, 0.0029164309894009134, 0.0030130694777831214, 0.0031121956230727955, 0.003213845010206586, 0.003318052624672616, 0.0034248528002906085, 0.003534279166052743, 0.0036463645920691633, 0.0037611411346649593, 0.0038786399806783195, 0.003998891391012432, 0.00412192464349661, 0.004247767975114953, 0.0043764485236637415, 0.004507992268901533, 0.0046424239732587745, 0.00477976712217646, 0.004920043864146036, 0.0050632749505254955, 0.005209479675209109, 0.005358675814230768, 0.005510879565383436, 0.005666105487939465, 0.005824366442558891, 0.005985673531474939, 0.006150036039048107, 0.0063174613727820786, 0.006487955004896619, 0.006661520414554313, 0.006838159030839568, 0.0070178701765897375, 0.007200651013179588, 0.007386496486361374, 0.007575399273263843, 0.0077673497306542764, 0.007962335844568335, 0.008160343181412896, 0.008361354840647449, 0.008565351409149572, 0.00877231091737005, 0.008982208797382775, 0.009195017842934177, 0.009410708171596123, 0.009629247189125369, 0.009850599556131497, 0.010074727157153912, 0.010301589072246911, 0.010531141551170058, 0.010763337990279074, 0.010998128912210215, 0.011235461948448692, 0.011475281824868948, 0.011717530350331776, 0.011962146408420072, 0.01220906595239174, 0.01245822200342467, 0.012709544652224925, 0.01296296106406537, 0.013218395487317664, 0.013475769265536262, 0.013735000853148428, 0.013996005834799456, 0.014258696948397421, 0.01452298411189651, 0.014788774453852823, 0.015055972347780855, 0.015324479450333491, 0.01559419474332229, 0.015865014579589134, 0.01613683273273416, 0.016409540450698784, 0.01668302651319626, 0.016957177292976036, 0.017231876820901517, 0.017507006854814478, 0.017782446952152715, 0.018058074546280917, 0.018333765026488123, 0.01860939182159837, 0.018884826487134514, 0.019159938795968574, 0.01943459683238516, 0.019708667089478053, 0.019982014569793396, 0.02025450288912642, 0.020525994383372263, 0.02079635021832506, 0.021065430502313257, 0.021333094401553034, 0.021599200258095815, 0.02186360571023976, 0.022126167815269906, 0.02238674317438578, 0.02264518805967022, 0.022901358542948013, 0.02315511062637814, 0.023406300374618723, 0.0236547840483995, 0.02390041823933236, 0.02414306000578686, 0.02438256700965382, 0.02461879765381692, 0.024851611220149287, 0.02508086800784923, 0.025306429471927034, 0.025528158361652602, 0.025745918858772126, 0.025959576715300386, 0.026168999390694562, 0.026374056188214413, 0.026574618390273603, 0.026770559392586914, 0.026961754836918376, 0.027148082742236273, 0.02732942363408195, 0.027505660671960867, 0.027676679774566282, 0.027842369742647952, 0.028002622379341046, 0.028157332607773172, 0.02830639858577082, 0.02844972181749017, 0.02858720726180099, 0.028718763437256954, 0.028844302523490076, 0.028963740458872005, 0.029076997034290324, 0.029183995982893302, 0.029284665065662692, 0.02937893615268013, 0.02946674529995916, 0.029548032821721682, 0.029622743358004387, 0.029690825937488025, 0.0297522340354497, 0.029806925626745914, 0.029854863233741962, 0.02989601396911107, 0.02993034957343494, 0.029957846447545455, 0.0299784856795558, 0.029992253066537564, 0.029999139130809132] + [0.03] * 2400 + [0.029999139130809132, 0.029992253066537564, 0.0299784856795558, 0.029957846447545455, 0.02993034957343494, 0.02989601396911107, 0.029854863233741962, 0.029806925626745914, 0.0297522340354497, 0.029690825937488025, 0.029622743358004387, 0.029548032821721682, 0.02946674529995916, 0.02937893615268013, 0.029284665065662692, 0.029183995982893302, 0.029076997034290324, 0.028963740458872005, 0.028844302523490076, 0.028718763437256954, 0.02858720726180099, 0.02844972181749017, 0.02830639858577082, 0.028157332607773172, 0.028002622379341046, 0.027842369742647952, 0.027676679774566282, 0.027505660671960867, 0.02732942363408195, 0.027148082742236273, 0.026961754836918376, 0.026770559392586914, 0.026574618390273603, 0.026374056188214413, 0.026168999390694562, 0.025959576715300386, 0.025745918858772126, 0.025528158361652602, 0.025306429471927034, 0.02508086800784923, 0.024851611220149287, 0.02461879765381692, 0.02438256700965382, 0.02414306000578686, 0.02390041823933236, 0.0236547840483995, 0.023406300374618723, 0.02315511062637814, 0.022901358542948013, 0.02264518805967022, 0.02238674317438578, 0.022126167815269906, 0.02186360571023976, 0.021599200258095815, 0.021333094401553034, 0.021065430502313257, 0.02079635021832506, 0.020525994383372263, 0.02025450288912642, 0.019982014569793396, 0.019708667089478053, 0.01943459683238516, 0.019159938795968574, 0.018884826487134514, 0.01860939182159837, 0.018333765026488123, 0.018058074546280917, 0.017782446952152715, 0.017507006854814478, 0.017231876820901517, 0.016957177292976036, 0.01668302651319626, 0.016409540450698784, 0.01613683273273416, 0.015865014579589134, 0.01559419474332229, 0.015324479450333491, 0.015055972347780855, 0.014788774453852823, 0.01452298411189651, 0.014258696948397421, 0.013996005834799456, 0.013735000853148428, 0.013475769265536262, 0.013218395487317664, 0.01296296106406537, 0.012709544652224925, 0.01245822200342467, 0.01220906595239174, 0.011962146408420072, 0.011717530350331776, 0.011475281824868948, 0.011235461948448692, 0.010998128912210215, 0.010763337990279074, 0.010531141551170058, 0.010301589072246911, 0.010074727157153912, 0.009850599556131497, 0.009629247189125369, 0.009410708171596123, 0.009195017842934177, 0.008982208797382775, 0.00877231091737005, 0.008565351409149572, 0.008361354840647449, 0.008160343181412896, 0.007962335844568335, 0.0077673497306542764, 0.007575399273263843, 0.007386496486361374, 0.007200651013179588, 0.0070178701765897375, 0.006838159030839568, 0.006661520414554313, 0.006487955004896619, 0.0063174613727820786, 0.006150036039048107, 0.005985673531474939, 0.005824366442558891, 0.005666105487939465, 0.005510879565383436, 0.005358675814230768, 0.005209479675209109, 0.0050632749505254955, 0.004920043864146036, 0.00477976712217646, 0.0046424239732587745, 0.004507992268901533, 0.0043764485236637415, 0.004247767975114953, 0.00412192464349661, 0.003998891391012432, 0.0038786399806783195, 0.0037611411346649593, 0.0036463645920691633, 0.003534279166052743, 0.0034248528002906085, 0.003318052624672616, 0.003213845010206586, 0.0031121956230727955, 0.0030130694777831214, 0.0029164309894009134, 0.0028222440247805333, 0.0027304719527883443, 0.0026410776934697776, 0.0025540237661298947, 0.002469272336297659, 0.0023867852615468304, 0.0023065241361491322, 0.0022284503345379554, 0.002152525053563493, 0.0020787093535227347, 0.0020069641979502434, 0.0019372504921580757, 0.0018695291205155869, 0.0018037609824621485, 0.0017399070272480768, 0.001677928287401205, 0.0016177859109186856, 0.0015594411921855662, 0.0015028556016237094, 0.001447990814076442, 0.001394808735936162, 0.001343271531023825, 0.0012933416452308927, 0.0012449818299358857, 0.001198155164209159, 0.0011528250758209412, 0.001108955361068983, 0.0010665102034434334, 0.0010254541911477047, 0.0009857523334951988, 0.0009473700762027662, 0.0009102733156027127, 0.0008744284117960341, 0.0008398022007703349, 0.0008063620055066135, 0.0007740756460997302, 0.000742911448917959, 0.0007128382548275099, 0.0006838254265083703, 0.0006558428548881647, 0.0006288609647210594, 0.0006028507193389735, 0.0005777836246025627, 0.0005536317320795551, 0.0005303676414781189, 0.0005079645023629436, 0.0004863960151817112, 0.0004656364316295382, 0.0004456605543788675, 0.0004264437362021095, 0.0004079618785141323, 0.0003901914293614473, 0.00037310938088465655, 0.0003566932662804085, 0.0003409211562887489, 0.00032577165523137104, 0.000311223896625865],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008720809757939942, 0.0023705618694456468, 0.005766215032202263, 0.012550916231803613, 0.024445846791109577, 0.04260688635143973, 0.06645070111356702, 0.09273942412977619, 0.11581752493633832, 0.12942829261084438] + [0.13123844921964034] * 32 + [0.12942829261084438, 0.11581752493633832, 0.09273942412977619, 0.06645070111356702, 0.04260688635143973, 0.024445846791109577, 0.012550916231803613, 0.005766215032202263, 0.0023705618694456468, 0.0008720809757939942],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005816880558200126, -0.00141475080123382, -0.0030364198768185603, -0.005727940737255914, -0.00944011975000529, -0.01346176608583226, -0.01632966743858337, -0.016278490553436206, -0.012197624710028023, -0.004543692735604421] + [0.0] * 32 + [0.004543692735604421, 0.012197624710028023, 0.016278490553436206, 0.01632966743858337, 0.01346176608583226, 0.00944011975000529, 0.005727940737255914, 0.0030364198768185603, 0.00141475080123382, 0.0005816880558200126],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00043027546606994526, 0.0011696099806496787, 0.0028449890885206483, 0.006192488405480169, 0.012061320466190116, 0.02102178397592465, 0.032786068250465775, 0.04575664422007058, 0.05714313338354751, 0.06385854120377411] + [0.06475165319695818] * 32 + [0.06385854120377411, 0.05714313338354751, 0.04575664422007058, 0.032786068250465775, 0.02102178397592465, 0.012061320466190116, 0.006192488405480169, 0.0028449890885206483, 0.0011696099806496787, 0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002869986919476152, -0.0006980229786798, -0.0014981372303101092, -0.002826104959003266, -0.004657654550360385, -0.00664189202319479, -0.008056884008399047, -0.008031633878285094, -0.00601817813107916, -0.0022418096068554105] + [0.0] * 32 + [0.0022418096068554105, 0.00601817813107916, 0.008031633878285094, 0.008056884008399047, 0.00664189202319479, 0.004657654550360385, 0.002826104959003266, 0.0014981372303101092, 0.0006980229786798, 0.0002869986919476152],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00043027546606994526, -0.0011696099806496787, -0.0028449890885206483, -0.006192488405480169, -0.012061320466190116, -0.02102178397592465, -0.032786068250465775, -0.04575664422007058, -0.05714313338354751, -0.06385854120377411] + [-0.06475165319695818] * 32 + [-0.06385854120377411, -0.05714313338354751, -0.04575664422007058, -0.032786068250465775, -0.02102178397592465, -0.012061320466190116, -0.006192488405480169, -0.0028449890885206483, -0.0011696099806496787, -0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002869986919476152, 0.0006980229786798, 0.0014981372303101092, 0.002826104959003266, 0.004657654550360385, 0.00664189202319479, 0.008056884008399047, 0.008031633878285094, 0.00601817813107916, 0.0022418096068554105] + [0.0] * 32 + [-0.0022418096068554105, -0.00601817813107916, -0.008031633878285094, -0.008056884008399047, -0.00664189202319479, -0.004657654550360385, -0.002826104959003266, -0.0014981372303101092, -0.0006980229786798, -0.0002869986919476152],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.000578814617958006, 0.0014077621782478478, 0.0030214204905466527, 0.0056996457058880136, 0.009393487199723162, 0.013395267301864666, 0.016249001720553706, 0.016198077640321433, 0.012137370564670113, 0.004521247683468351] + [0.0] * 32 + [-0.004521247683468351, -0.012137370564670113, -0.016198077640321433, -0.016249001720553706, -0.013395267301864666, -0.009393487199723162, -0.0056996457058880136, -0.0030214204905466527, -0.0014077621782478478, -0.000578814617958006],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008677730473957577, 0.002358851705962418, 0.005737730932471792, 0.01248891688775228, 0.02432508855817774, 0.042396415740603745, 0.06612244620335157, 0.09228130749848398, 0.11524540649947819, 0.1287889393480744] + [0.13059015409794128] * 32 + [0.1287889393480744, 0.11524540649947819, 0.09228130749848398, 0.06612244620335157, 0.042396415740603745, 0.02432508855817774, 0.01248891688775228, 0.005737730932471792, 0.002358851705962418, 0.0008677730473957577],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002869986919476152, 0.0006980229786798, 0.0014981372303101092, 0.002826104959003266, 0.004657654550360385, 0.00664189202319479, 0.008056884008399047, 0.008031633878285094, 0.00601817813107916, 0.0022418096068554105] + [0.0] * 32 + [-0.0022418096068554105, -0.00601817813107916, -0.008031633878285094, -0.008056884008399047, -0.00664189202319479, -0.004657654550360385, -0.002826104959003266, -0.0014981372303101092, -0.0006980229786798, -0.0002869986919476152],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00043027546606994526, 0.0011696099806496787, 0.0028449890885206483, 0.006192488405480169, 0.012061320466190116, 0.02102178397592465, 0.032786068250465775, 0.04575664422007058, 0.05714313338354751, 0.06385854120377411] + [0.06475165319695818] * 32 + [0.06385854120377411, 0.05714313338354751, 0.04575664422007058, 0.032786068250465775, 0.02102178397592465, 0.012061320466190116, 0.006192488405480169, 0.0028449890885206483, 0.0011696099806496787, 0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00015601692710188027, 0.00037945608546537004, 0.0008144105656501313, 0.0015363143587133643, 0.002531973039730627, 0.0036106352142903976, 0.004379846738939619, 0.00436612037774066, 0.003271574697399972, 0.0012186823697192873] + [0.0] * 32 + [-0.0012186823697192873, -0.003271574697399972, -0.00436612037774066, -0.004379846738939619, -0.0036106352142903976, -0.002531973039730627, -0.0015363143587133643, -0.0008144105656501313, -0.00037945608546537004, -0.00015601692710188027],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00023390439715249725, 0.0006358180723763009, 0.0015465800635439412, 0.0033663324581053593, 0.006556720322159072, 0.011427766851013911, 0.017823013706013142, 0.02487401938059161, 0.03106389097097776, 0.034714490509385854] + [0.0352] * 32 + [0.034714490509385854, 0.03106389097097776, 0.02487401938059161, 0.017823013706013142, 0.011427766851013911, 0.006556720322159072, 0.0033663324581053593, 0.0015465800635439412, 0.0006358180723763009, 0.00023390439715249725],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00023390439715249725, 0.0006358180723763009, 0.0015465800635439412, 0.0033663324581053593, 0.006556720322159072, 0.011427766851013911, 0.017823013706013142, 0.02487401938059161, 0.03106389097097776, 0.034714490509385854] + [0.0352] * 32 + [0.034714490509385854, 0.03106389097097776, 0.02487401938059161, 0.017823013706013142, 0.011427766851013911, 0.006556720322159072, 0.0033663324581053593, 0.0015465800635439412, 0.0006358180723763009, 0.00023390439715249725],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00015601692710188027, -0.00037945608546537004, -0.0008144105656501313, -0.0015363143587133643, -0.002531973039730627, -0.0036106352142903976, -0.004379846738939619, -0.00436612037774066, -0.003271574697399972, -0.0012186823697192873] + [0.0] * 32 + [0.0012186823697192873, 0.003271574697399972, 0.00436612037774066, 0.004379846738939619, 0.0036106352142903976, 0.002531973039730627, 0.0015363143587133643, 0.0008144105656501313, 0.00037945608546537004, 0.00015601692710188027],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002869986919476152, -0.0006980229786798, -0.0014981372303101092, -0.002826104959003266, -0.004657654550360385, -0.00664189202319479, -0.008056884008399047, -0.008031633878285094, -0.00601817813107916, -0.0022418096068554105] + [0.0] * 32 + [0.0022418096068554105, 0.00601817813107916, 0.008031633878285094, 0.008056884008399047, 0.00664189202319479, 0.004657654550360385, 0.002826104959003266, 0.0014981372303101092, 0.0006980229786798, 0.0002869986919476152],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q5_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00043027546606994526, -0.0011696099806496787, -0.0028449890885206483, -0.006192488405480169, -0.012061320466190116, -0.02102178397592465, -0.032786068250465775, -0.04575664422007058, -0.05714313338354751, -0.06385854120377411] + [-0.06475165319695818] * 32 + [-0.06385854120377411, -0.05714313338354751, -0.04575664422007058, -0.032786068250465775, -0.02102178397592465, -0.012061320466190116, -0.006192488405480169, -0.0028449890885206483, -0.0011696099806496787, -0.00043027546606994526],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 76 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008885405042653874, 0.0024153035065944393, 0.005875045729269468, 0.012787800384529636, 0.024907234119160446, 0.043411042477355034, 0.06770488190328897, 0.09448977442321642, 0.11800344792065792, 0.13187110322862264] + [0.13371542446784532] * 76 + [0.13187110322862264, 0.11800344792065792, 0.09448977442321642, 0.06770488190328897, 0.043411042477355034, 0.024907234119160446, 0.012787800384529636, 0.005875045729269468, 0.0024153035065944393, 0.0008885405042653874],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.002618373842072091, 0.0071174780350170596, 0.0173127347427056, 0.037683416640836805, 0.0733972733746041, 0.12792476823975737, 0.1995144744726272, 0.27844487955852, 0.3477355729159673, 0.3886011336134702] + [0.3940360265260349] * 76 + [0.3886011336134702, 0.3477355729159673, 0.27844487955852, 0.1995144744726272, 0.12792476823975737, 0.0733972733746041, 0.037683416640836805, 0.0173127347427056, 0.0071174780350170596, 0.002618373842072091],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.002618373842072091, 0.0071174780350170596, 0.0173127347427056, 0.037683416640836805, 0.0733972733746041, 0.12792476823975737, 0.1995144744726272, 0.27844487955852, 0.3477355729159673, 0.3886011336134702] + [0.3940360265260349] * 76 + [0.3886011336134702, 0.3477355729159673, 0.27844487955852, 0.1995144744726272, 0.12792476823975737, 0.0733972733746041, 0.037683416640836805, 0.0173127347427056, 0.0071174780350170596, 0.002618373842072091],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004395104015456173, 0.0011947131379401897, 0.0029060506472970626, 0.006325396821990164, 0.012320190713369306, 0.021472971259211725, 0.033489750539301665, 0.04673871196568297, 0.058369587576938574, 0.06522912715182705] + [0.06614140786895659] * 76 + [0.06522912715182705, 0.058369587576938574, 0.04673871196568297, 0.033489750539301665, 0.021472971259211725, 0.012320190713369306, 0.006325396821990164, 0.0029060506472970626, 0.0011947131379401897, 0.0004395104015456173],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0004395104015456173, -0.0011947131379401897, -0.0029060506472970626, -0.006325396821990164, -0.012320190713369306, -0.021472971259211725, -0.033489750539301665, -0.04673871196568297, -0.058369587576938574, -0.06522912715182705] + [-0.06614140786895659] * 76 + [-0.06522912715182705, -0.058369587576938574, -0.04673871196568297, -0.033489750539301665, -0.021472971259211725, -0.012320190713369306, -0.006325396821990164, -0.0029060506472970626, -0.0011947131379401897, -0.0004395104015456173],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008903554366180133, 0.002420237004228465, 0.005887046094493137, 0.012813920738667, 0.024958109622078197, 0.04349971384920038, 0.06784317585838401, 0.09468277918526134, 0.11824448169944966, 0.13214046307263333] + [0.13398855152142003] * 76 + [0.13214046307263333, 0.11824448169944966, 0.09468277918526134, 0.06784317585838401, 0.04349971384920038, 0.024958109622078197, 0.012813920738667, 0.005887046094493137, 0.002420237004228465, 0.0008903554366180133],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004395066070840293, 0.0011947028235242063, 0.0029060255582490785, 0.006325342212417363, 0.012320084348445394, 0.0214727858748287, 0.03348946140946181, 0.04673830845248601, 0.058369083649938924, 0.06522856400379569] + [0.06614083684485647] * 76 + [0.06522856400379569, 0.058369083649938924, 0.04673830845248601, 0.03348946140946181, 0.0214727858748287, 0.012320084348445394, 0.006325342212417363, 0.0029060255582490785, 0.0011947028235242063, 0.0004395066070840293],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0004395066070840293, -0.0011947028235242063, -0.0029060255582490785, -0.006325342212417363, -0.012320084348445394, -0.0214727858748287, -0.03348946140946181, -0.04673830845248601, -0.058369083649938924, -0.06522856400379569] + [-0.06614083684485647] * 76 + [-0.06522856400379569, -0.058369083649938924, -0.04673830845248601, -0.03348946140946181, -0.0214727858748287, -0.012320084348445394, -0.006325342212417363, -0.0029060255582490785, -0.0011947028235242063, -0.0004395066070840293],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0002074825977505767, 0.00021718110348758075, 0.000227280770859166, 0.00023779551085360574, 0.00024873958725643775, 0.00026012761957429825, 0.00027197458567608827, 0.00028429582413473973, 0.00029710703625257837, 0.0003104242877530255, 0.00032426401012114085, 0.00033864300157529585, 0.00035357842765207934, 0.0003690878213863702, 0.00038518908306837523, 0.00040190047955931577, 0.00041924064314737306, 0.0004372285699254432, 0.000455883617672247, 0.0004752255032183401, 0.0004952742992786395, 0.0005160504307331536, 0.0005375746703377424, 0.00055986813384689, 0.0005829522745306895, 0.0006068488770684752, 0.0006315800508018443, 0.0006571682223301327, 0.0006836361274318032, 0.0007110068022956224, 0.0007393035740459889, 0.0007685500505472943, 0.0007987701094727728, 0.0008299878866239239, 0.000862227763487262, 0.0008955143540158835, 0.0009298724906241083, 0.0009653272093842949, 0.0010019037344158065, 0.0010396274614570445, 0.0010785239406124573, 0.0011186188582674702, 0.0011599380181653847, 0.0012025073216414327, 0.0012463527470103915, 0.0012915003281053841, 0.0013379761319668292, 0.0013858062356818235, 0.001435016702375662, 0.0014856335563586374, 0.001537682757432755, 0.001591190174364554, 0.0016461815575317732, 0.0017026825107532635, 0.0017607184623131857, 0.0018203146351922297, 0.001881496016520356, 0.0019442873262672763, 0.002008712985188748, 0.002074797082048531, 0.0021425633401377245, 0.0022120350831150775, 0.0022832352001937394, 0.0023561861107018293, 0.0024309097280461093, 0.0025074274231099737, 0.00258575998711888, 0.002665927594008288, 0.002747949762331074, 0.002831845316743303, 0.0029176323491091616, 0.003005328179267689, 0.0030949493155058507, 0.003186511414784307, 0.0032800292427640244, 0.0033755166336836644, 0.0034729864501394066, 0.003572450542820513, 0.003673919710255625, 0.003777403658626311, 0.003882910961705928, 0.003990449020983293, 0.004100024026032072, 0.004211640915188053, 0.004325303336597747, 0.0044410136097028765, 0.00455877268722638, 0.0046785801177264925, 0.004800434008786394, 0.004924330990907584, 0.005050266182175896, 0.005178233153769519, 0.00530822389637889, 0.005440228787608598, 0.005574236560431633, 0.005710234272766382, 0.005848207278246701, 0.005988139198255185, 0.006130011895289452, 0.00627380544773075, 0.00641949812608358, 0.0065670663707543325, 0.006716484771435942, 0.006867726048164609, 0.007020761034113373, 0.00717555866018605, 0.007332085941473478, 0.007490307965632463, 0.007650187883245967, 0.007811686900221186, 0.00797476427228005, 0.008139377301594496, 0.008305481335616448, 0.008473029768149952, 0.008641974042710249, 0.008812263658211777, 0.008983846177024177, 0.009156667235432287, 0.009330670556532972, 0.009505797965598282, 0.009681989407931009, 0.009859182969235217, 0.010037314898520572, 0.010216319633555664, 0.010396129828881528, 0.010576676386392758, 0.010757888488489442, 0.010939693633799192, 0.011122017675464176, 0.011304784861984028, 0.011487917880601016, 0.011671337903209655, 0.011854964634768478, 0.01203871636418728, 0.012222510017658752, 0.012406261214398915, 0.012589884324756344, 0.012773292530645719, 0.012956397888256777, 0.013139111392985372, 0.013321343046528933, 0.013503001926084283, 0.013683996255581513, 0.013864233478883378, 0.014043620334875507, 0.014222062934368694, 0.014399466838730546, 0.014575737140159844, 0.014750778543513275, 0.014924495449590524, 0.01509679203978015, 0.015267572361965345, 0.015436740417585429, 0.01560420024974582, 0.015769856032266338, 0.01593361215955491, 0.016095373337191243, 0.016255044673102553, 0.016412531769211283, 0.01656774081343286, 0.01672057867189949, 0.016870952981284694, 0.01701877224110174, 0.017163945905848087, 0.01730638447686693, 0.017445999593796377, 0.01758270412547628, 0.017716412260182408, 0.017847039595057946, 0.017974503224612255, 0.01809872182815752, 0.018219615756054637, 0.018337107114640584, 0.01845111984971086, 0.018561579828431974, 0.018668414919560703, 0.018771555071848786, 0.018870932390513885, 0.018966481211660117, 0.019058138174533997, 0.019145842291504643, 0.019229535015660056, 0.019309160305914674, 0.019384664689526886, 0.01945599732192887, 0.019523110043775133, 0.01958595743512009, 0.019644496866639445, 0.01969868854781446, 0.01974849557200293, 0.019793883958325355, 0.019834822690299805, 0.019871283751163947, 0.01990324215582798, 0.019930675979407387, 0.019953566382289963, 0.019971897631696975, 0.019985657119703872, 0.019994835377691714, 0.019999426087206094] + [0.020000000000000004] * 2800 + [0.019999426087206094, 0.019994835377691714, 0.019985657119703872, 0.019971897631696975, 0.019953566382289963, 0.019930675979407387, 0.01990324215582798, 0.019871283751163947, 0.019834822690299805, 0.019793883958325355, 0.01974849557200293, 0.01969868854781446, 0.019644496866639445, 0.01958595743512009, 0.019523110043775133, 0.01945599732192887, 0.019384664689526886, 0.019309160305914674, 0.019229535015660056, 0.019145842291504643, 0.019058138174533997, 0.018966481211660117, 0.018870932390513885, 0.018771555071848786, 0.018668414919560703, 0.018561579828431974, 0.01845111984971086, 0.018337107114640584, 0.018219615756054637, 0.01809872182815752, 0.017974503224612255, 0.017847039595057946, 0.017716412260182408, 0.01758270412547628, 0.017445999593796377, 0.01730638447686693, 0.017163945905848087, 0.01701877224110174, 0.016870952981284694, 0.01672057867189949, 0.01656774081343286, 0.016412531769211283, 0.016255044673102553, 0.016095373337191243, 0.01593361215955491, 0.015769856032266338, 0.01560420024974582, 0.015436740417585429, 0.015267572361965345, 0.01509679203978015, 0.014924495449590524, 0.014750778543513275, 0.014575737140159844, 0.014399466838730546, 0.014222062934368694, 0.014043620334875507, 0.013864233478883378, 0.013683996255581513, 0.013503001926084283, 0.013321343046528933, 0.013139111392985372, 0.012956397888256777, 0.012773292530645719, 0.012589884324756344, 0.012406261214398915, 0.012222510017658752, 0.01203871636418728, 0.011854964634768478, 0.011671337903209655, 0.011487917880601016, 0.011304784861984028, 0.011122017675464176, 0.010939693633799192, 0.010757888488489442, 0.010576676386392758, 0.010396129828881528, 0.010216319633555664, 0.010037314898520572, 0.009859182969235217, 0.009681989407931009, 0.009505797965598282, 0.009330670556532972, 0.009156667235432287, 0.008983846177024177, 0.008812263658211777, 0.008641974042710249, 0.008473029768149952, 0.008305481335616448, 0.008139377301594496, 0.00797476427228005, 0.007811686900221186, 0.007650187883245967, 0.007490307965632463, 0.007332085941473478, 0.00717555866018605, 0.007020761034113373, 0.006867726048164609, 0.006716484771435942, 0.0065670663707543325, 0.00641949812608358, 0.00627380544773075, 0.006130011895289452, 0.005988139198255185, 0.005848207278246701, 0.005710234272766382, 0.005574236560431633, 0.005440228787608598, 0.00530822389637889, 0.005178233153769519, 0.005050266182175896, 0.004924330990907584, 0.004800434008786394, 0.0046785801177264925, 0.00455877268722638, 0.0044410136097028765, 0.004325303336597747, 0.004211640915188053, 0.004100024026032072, 0.003990449020983293, 0.003882910961705928, 0.003777403658626311, 0.003673919710255625, 0.003572450542820513, 0.0034729864501394066, 0.0033755166336836644, 0.0032800292427640244, 0.003186511414784307, 0.0030949493155058507, 0.003005328179267689, 0.0029176323491091616, 0.002831845316743303, 0.002747949762331074, 0.002665927594008288, 0.00258575998711888, 0.0025074274231099737, 0.0024309097280461093, 0.0023561861107018293, 0.0022832352001937394, 0.0022120350831150775, 0.0021425633401377245, 0.002074797082048531, 0.002008712985188748, 0.0019442873262672763, 0.001881496016520356, 0.0018203146351922297, 0.0017607184623131857, 0.0017026825107532635, 0.0016461815575317732, 0.001591190174364554, 0.001537682757432755, 0.0014856335563586374, 0.001435016702375662, 0.0013858062356818235, 0.0013379761319668292, 0.0012915003281053841, 0.0012463527470103915, 0.0012025073216414327, 0.0011599380181653847, 0.0011186188582674702, 0.0010785239406124573, 0.0010396274614570445, 0.0010019037344158065, 0.0009653272093842949, 0.0009298724906241083, 0.0008955143540158835, 0.000862227763487262, 0.0008299878866239239, 0.0007987701094727728, 0.0007685500505472943, 0.0007393035740459889, 0.0007110068022956224, 0.0006836361274318032, 0.0006571682223301327, 0.0006315800508018443, 0.0006068488770684752, 0.0005829522745306895, 0.00055986813384689, 0.0005375746703377424, 0.0005160504307331536, 0.0004952742992786395, 0.0004752255032183401, 0.000455883617672247, 0.0004372285699254432, 0.00041924064314737306, 0.00040190047955931577, 0.00038518908306837523, 0.0003690878213863702, 0.00035357842765207934, 0.00033864300157529585, 0.00032426401012114085, 0.0003104242877530255, 0.00029710703625257837, 0.00028429582413473973, 0.00027197458567608827, 0.00026012761957429825, 0.00024873958725643775, 0.00023779551085360574, 0.000227280770859166, 0.00021718110348758075, 0.0002074825977505767],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008885405042653874, 0.0024153035065944393, 0.005875045729269468, 0.012787800384529636, 0.024907234119160446, 0.043411042477355034, 0.06770488190328897, 0.09448977442321642, 0.11800344792065792, 0.13187110322862264] + [0.13371542446784532] * 76 + [0.13187110322862264, 0.11800344792065792, 0.09448977442321642, 0.06770488190328897, 0.043411042477355034, 0.024907234119160446, 0.012787800384529636, 0.005875045729269468, 0.0024153035065944393, 0.0008885405042653874],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00019416955659326259, 0.0004722488849771615, 0.0010135678310975295, 0.001912007135126054, 0.0031511457863129906, 0.004493585738430667, 0.005450901482574475, 0.005433818455000804, 0.004071610819132933, 0.001516700910292244] + [0.0] * 76 + [-0.001516700910292244, -0.004071610819132933, -0.005433818455000804, -0.005450901482574475, -0.004493585738430667, -0.0031511457863129906, -0.001912007135126054, -0.0010135678310975295, -0.0004722488849771615, -0.00019416955659326259],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004395104015456173, 0.0011947131379401897, 0.0029060506472970626, 0.006325396821990164, 0.012320190713369306, 0.021472971259211725, 0.033489750539301665, 0.04673871196568297, 0.058369587576938574, 0.06522912715182705] + [0.06614140786895659] * 76 + [0.06522912715182705, 0.058369587576938574, 0.04673871196568297, 0.033489750539301665, 0.021472971259211725, 0.012320190713369306, 0.006325396821990164, 0.0029060506472970626, 0.0011947131379401897, 0.0004395104015456173],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [9.604462528896742e-05, 0.00023359463757635204, 0.000501354302140336, 0.0009457610763755844, 0.0015586924211364315, 0.0022227210383731016, 0.002696250635611269, 0.0026878006344323957, 0.0020139940694477404, 0.0007502255923136251] + [0.0] * 76 + [-0.0007502255923136251, -0.0020139940694477404, -0.0026878006344323957, -0.002696250635611269, -0.0022227210383731016, -0.0015586924211364315, -0.0009457610763755844, -0.000501354302140336, -0.00023359463757635204, -9.604462528896742e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0004395104015456173, -0.0011947131379401897, -0.0029060506472970626, -0.006325396821990164, -0.012320190713369306, -0.021472971259211725, -0.033489750539301665, -0.04673871196568297, -0.058369587576938574, -0.06522912715182705] + [-0.06614140786895659] * 76 + [-0.06522912715182705, -0.058369587576938574, -0.04673871196568297, -0.033489750539301665, -0.021472971259211725, -0.012320190713369306, -0.006325396821990164, -0.0029060506472970626, -0.0011947131379401897, -0.0004395104015456173],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [-9.604462528896742e-05, -0.00023359463757635204, -0.000501354302140336, -0.0009457610763755844, -0.0015586924211364315, -0.0022227210383731016, -0.002696250635611269, -0.0026878006344323957, -0.0020139940694477404, -0.0007502255923136251] + [0.0] * 76 + [0.0007502255923136251, 0.0020139940694477404, 0.0026878006344323957, 0.002696250635611269, 0.0022227210383731016, 0.0015586924211364315, 0.0009457610763755844, 0.000501354302140336, 0.00023359463757635204, 9.604462528896742e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00019456616722436429, -0.00047321350029376453, -0.0010156381442002064, -0.0019159125998643902, -0.00315758231498891, -0.004502764334225484, -0.005462035490989635, -0.005444917569633097, -0.004079927489186208, -0.0015197989227499005] + [0.0] * 76 + [0.0015197989227499005, 0.004079927489186208, 0.005444917569633097, 0.005462035490989635, 0.004502764334225484, 0.00315758231498891, 0.0019159125998643902, 0.0010156381442002064, 0.00047321350029376453, 0.00019456616722436429],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008903554366180133, 0.002420237004228465, 0.005887046094493137, 0.012813920738667, 0.024958109622078197, 0.04349971384920038, 0.06784317585838401, 0.09468277918526134, 0.11824448169944966, 0.13214046307263333] + [0.13398855152142003] * 76 + [0.13214046307263333, 0.11824448169944966, 0.09468277918526134, 0.06784317585838401, 0.04349971384920038, 0.024958109622078197, 0.012813920738667, 0.005887046094493137, 0.002420237004228465, 0.0008903554366180133],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [-9.604379609894118e-05, -0.00023359262086440093, -0.0005013499737566738, -0.0009457529112580738, -0.0015586789643479261, -0.0022227018487712825, -0.0026962273578471194, -0.002687777429620342, -0.0020139766818657676, -0.0007502191153288203] + [0.0] * 76 + [0.0007502191153288203, 0.0020139766818657676, 0.002687777429620342, 0.0026962273578471194, 0.0022227018487712825, 0.0015586789643479261, 0.0009457529112580738, 0.0005013499737566738, 0.00023359262086440093, 9.604379609894118e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004395066070840293, 0.0011947028235242063, 0.0029060255582490785, 0.006325342212417363, 0.012320084348445394, 0.0214727858748287, 0.03348946140946181, 0.04673830845248601, 0.058369083649938924, 0.06522856400379569] + [0.06614083684485647] * 76 + [0.06522856400379569, 0.058369083649938924, 0.04673830845248601, 0.03348946140946181, 0.0214727858748287, 0.012320084348445394, 0.006325342212417363, 0.0029060255582490785, 0.0011947028235242063, 0.0004395066070840293],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005721838064443316, -0.0013916350705860325, -0.002986807560681391, -0.0056343514386081065, -0.009285876850666641, -0.013241813173551003, -0.01606285564830268, -0.016012514946525353, -0.01199832670850443, -0.004469452963249501] + [0.0] * 76 + [0.004469452963249501, 0.01199832670850443, 0.016012514946525353, 0.01606285564830268, 0.013241813173551003, 0.009285876850666641, 0.0056343514386081065, 0.002986807560681391, 0.0013916350705860325, 0.0005721838064443316],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.002618373842072091, 0.0071174780350170596, 0.0173127347427056, 0.037683416640836805, 0.0733972733746041, 0.12792476823975737, 0.1995144744726272, 0.27844487955852, 0.3477355729159673, 0.3886011336134702] + [0.3940360265260349] * 76 + [0.3886011336134702, 0.3477355729159673, 0.27844487955852, 0.1995144744726272, 0.12792476823975737, 0.0733972733746041, 0.037683416640836805, 0.0173127347427056, 0.0071174780350170596, 0.002618373842072091],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.002618373842072091, 0.0071174780350170596, 0.0173127347427056, 0.037683416640836805, 0.0733972733746041, 0.12792476823975737, 0.1995144744726272, 0.27844487955852, 0.3477355729159673, 0.3886011336134702] + [0.3940360265260349] * 76 + [0.3886011336134702, 0.3477355729159673, 0.27844487955852, 0.1995144744726272, 0.12792476823975737, 0.0733972733746041, 0.037683416640836805, 0.0173127347427056, 0.0071174780350170596, 0.002618373842072091],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005721838064443316, 0.0013916350705860325, 0.002986807560681391, 0.0056343514386081065, 0.009285876850666641, 0.013241813173551003, 0.01606285564830268, 0.016012514946525353, 0.01199832670850443, 0.004469452963249501] + [0.0] * 76 + [-0.004469452963249501, -0.01199832670850443, -0.016012514946525353, -0.01606285564830268, -0.013241813173551003, -0.009285876850666641, -0.0056343514386081065, -0.002986807560681391, -0.0013916350705860325, -0.0005721838064443316],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [9.604379609894118e-05, 0.00023359262086440093, 0.0005013499737566738, 0.0009457529112580738, 0.0015586789643479261, 0.0022227018487712825, 0.0026962273578471194, 0.002687777429620342, 0.0020139766818657676, 0.0007502191153288203] + [0.0] * 76 + [-0.0007502191153288203, -0.0020139766818657676, -0.002687777429620342, -0.0026962273578471194, -0.0022227018487712825, -0.0015586789643479261, -0.0009457529112580738, -0.0005013499737566738, -0.00023359262086440093, -9.604379609894118e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q6_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0004395066070840293, -0.0011947028235242063, -0.0029060255582490785, -0.006325342212417363, -0.012320084348445394, -0.0214727858748287, -0.03348946140946181, -0.04673830845248601, -0.058369083649938924, -0.06522856400379569] + [-0.06614083684485647] * 76 + [-0.06522856400379569, -0.058369083649938924, -0.04673830845248601, -0.03348946140946181, -0.0214727858748287, -0.012320084348445394, -0.006325342212417363, -0.0029060255582490785, -0.0011947028235242063, -0.0004395066070840293],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 492 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.00011257974777361855, 0.0003060234826255299, 0.0007443793087479585, 0.0016202382839710565, 0.0031557932603104395, 0.005500260471221883, 0.008578335473875393, 0.011972031573897268, 0.014951258090714032, 0.016708316018054] + [0.016941994976895476] * 492 + [0.016708316018054, 0.014951258090714032, 0.011972031573897268, 0.008578335473875393, 0.005500260471221883, 0.0031557932603104395, 0.0016202382839710565, 0.0007443793087479585, 0.0003060234826255299, 0.00011257974777361855],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 492 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 492 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [5.6381512762923065e-05, 0.0001532608416044855, 0.0003727955722642306, 0.0008114380010016118, 0.0015804654167561976, 0.002754607396893355, 0.004296150422876324, 0.005995760910205055, 0.00748779923151408, 0.008367758424127658] + [0.00848478811606515] * 492 + [0.008367758424127658, 0.00748779923151408, 0.005995760910205055, 0.004296150422876324, 0.002754607396893355, 0.0015804654167561976, 0.0008114380010016118, 0.0003727955722642306, 0.0001532608416044855, 5.6381512762923065e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-5.6381512762923065e-05, -0.0001532608416044855, -0.0003727955722642306, -0.0008114380010016118, -0.0015804654167561976, -0.002754607396893355, -0.004296150422876324, -0.005995760910205055, -0.00748779923151408, -0.008367758424127658] + [-0.00848478811606515] * 492 + [-0.008367758424127658, -0.00748779923151408, -0.005995760910205055, -0.004296150422876324, -0.002754607396893355, -0.0015804654167561976, -0.0008114380010016118, -0.0003727955722642306, -0.0001532608416044855, -5.6381512762923065e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00011262973261513518, 0.000306159355511923, 0.0007447098094153684, 0.0016209576616161932, 0.0031571944166382464, 0.00550270255919411, 0.008582144211660099, 0.011977347095673498, 0.014957896374072433, 0.016715734426290724] + [0.016949517137414067] * 492 + [0.016715734426290724, 0.014957896374072433, 0.011977347095673498, 0.008582144211660099, 0.00550270255919411, 0.0031571944166382464, 0.0016209576616161932, 0.0007447098094153684, 0.000306159355511923, 0.00011262973261513518],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [5.628987388680927e-05, 0.00015301174131276496, 0.00037218965437397925, 0.0008101191419855282, 0.0015778966301552197, 0.0027501302356109417, 0.004289167736937697, 0.005986015786948634, 0.007475629045357016, 0.008354158009027] + [0.008470997488447738] * 492 + [0.008354158009027, 0.007475629045357016, 0.005986015786948634, 0.004289167736937697, 0.0027501302356109417, 0.0015778966301552197, 0.0008101191419855282, 0.00037218965437397925, 0.00015301174131276496, 5.628987388680927e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-5.628987388680927e-05, -0.00015301174131276496, -0.00037218965437397925, -0.0008101191419855282, -0.0015778966301552197, -0.0027501302356109417, -0.004289167736937697, -0.005986015786948634, -0.007475629045357016, -0.008354158009027] + [-0.008470997488447738] * 492 + [-0.008354158009027, -0.007475629045357016, -0.005986015786948634, -0.004289167736937697, -0.0027501302356109417, -0.0015778966301552197, -0.0008101191419855282, -0.00037218965437397925, -0.00015301174131276496, -5.628987388680927e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0004149651955011534, 0.0004343622069751615, 0.000454561541718332, 0.0004755910217072115, 0.0004974791745128755, 0.0005202552391485965, 0.0005439491713521765, 0.0005685916482694795, 0.0005942140725051567, 0.000620848575506051, 0.0006485280202422817, 0.0006772860031505917, 0.0007071568553041587, 0.0007381756427727404, 0.0007703781661367505, 0.0008038009591186315, 0.0008384812862947461, 0.0008744571398508864, 0.000911767235344494, 0.0009504510064366802, 0.000990548598557279, 0.0010321008614663071, 0.0010751493406754849, 0.00111973626769378, 0.001165904549061379, 0.0012136977541369505, 0.0012631601016036885, 0.0013143364446602654, 0.0013672722548636065, 0.0014220136045912449, 0.0014786071480919778, 0.0015371001010945887, 0.0015975402189455457, 0.0016599757732478479, 0.001724455526974524, 0.001791028708031767, 0.0018597449812482166, 0.0019306544187685899, 0.002003807468831613, 0.002079254922914089, 0.0021570478812249147, 0.0022372377165349403, 0.0023198760363307694, 0.0024050146432828654, 0.002492705494020783, 0.0025830006562107682, 0.0026759522639336585, 0.002771612471363647, 0.002870033404751324, 0.002971267112717275, 0.00307536551486551, 0.003182380348729108, 0.0032923631150635463, 0.003405365021506527, 0.0035214369246263713, 0.0036406292703844594, 0.003762992033040712, 0.0038885746525345525, 0.004017425970377496, 0.004149594164097062, 0.004285126680275449, 0.004424070166230155, 0.004566470400387479, 0.004712372221403659, 0.0048618194560922185, 0.005014854846219947, 0.00517151997423776, 0.005331855188016576, 0.005495899524662148, 0.005663690633486606, 0.005835264698218323, 0.006010656358535378, 0.006189898631011701, 0.006373022829568614, 0.006560058485528049, 0.006751033267367329, 0.006945972900278813, 0.007144901085641026, 0.00734783942051125, 0.007554807317252622, 0.007765821923411856, 0.007980898041966587, 0.008200048052064144, 0.008423281830376106, 0.008650606673195494, 0.008882027219405753, 0.00911754537445276, 0.009357160235452985, 0.009600868017572787, 0.009848661981815167, 0.010100532364351792, 0.010356466307539038, 0.01061644779275778, 0.010880457575217196, 0.011148473120863266, 0.011420468545532764, 0.011696414556493402, 0.01197627839651037, 0.012260023790578905, 0.0125476108954615, 0.01283899625216716, 0.013134132741508665, 0.013432969542871884, 0.013735452096329218, 0.014041522068226746, 0.0143511173203721, 0.014664171882946955, 0.014980615931264925, 0.015300375766491934, 0.015623373800442372, 0.0159495285445601, 0.01627875460318899, 0.016610962671232896, 0.016946059536299903, 0.017283948085420497, 0.017624527316423555, 0.017967692354048354, 0.018313334470864574, 0.018661341113065943, 0.019011595931196563, 0.019363978815862017, 0.019718365938470435, 0.020074629797041145, 0.02043263926711133, 0.020792259657763056, 0.021153352772785516, 0.021515776976978884, 0.021879387267598385, 0.02224403535092835, 0.022609569723968055, 0.022975835761202032, 0.02334267580641931, 0.023709929269536956, 0.02407743272837456, 0.024445020035317504, 0.02481252242879783, 0.02517976864951269, 0.025546585061291437, 0.025912795776513554, 0.026278222785970744, 0.026642686093057866, 0.027006003852168566, 0.027367992511163026, 0.027728466957766755, 0.028087240669751014, 0.028444125868737388, 0.028798933677461093, 0.029151474280319688, 0.02950155708702655, 0.029848990899181048, 0.0301935840795603, 0.03053514472393069, 0.030873480835170858, 0.03120840049949164, 0.031539712064532675, 0.03186722431910982, 0.03219074667438249, 0.032510089346205105, 0.032825063538422565, 0.03313548162686572, 0.03344115734379898, 0.03374190596256939, 0.03403754448220348, 0.034327891811696175, 0.03461276895373386, 0.034891999187592754, 0.03516540825095256, 0.035432824520364815, 0.03569407919011589, 0.03594900644922451, 0.03619744365631504, 0.036439231512109274, 0.03667421422928117, 0.03690223969942172, 0.03712315965686395, 0.037336829839121406, 0.03754311014369757, 0.03774186478102777, 0.037932962423320234, 0.038116276349067994, 0.038291684583009286, 0.03845907003132011, 0.03861832061182935, 0.03876932937905377, 0.03891199464385774, 0.039046220087550265, 0.03917191487024018, 0.03928899373327889, 0.03939737709562892, 0.03949699114400586, 0.03958776791665071, 0.03966964538059961, 0.039742567502327894, 0.03980648431165596, 0.039861351958814774, 0.039907132764579925, 0.03994379526339395, 0.039971314239407744, 0.03998967075538343, 0.03999885217441219] + [0.04000000000000001] * 2800 + [0.03999885217441219, 0.03998967075538343, 0.039971314239407744, 0.03994379526339395, 0.039907132764579925, 0.039861351958814774, 0.03980648431165596, 0.039742567502327894, 0.03966964538059961, 0.03958776791665071, 0.03949699114400586, 0.03939737709562892, 0.03928899373327889, 0.03917191487024018, 0.039046220087550265, 0.03891199464385774, 0.03876932937905377, 0.03861832061182935, 0.03845907003132011, 0.038291684583009286, 0.038116276349067994, 0.037932962423320234, 0.03774186478102777, 0.03754311014369757, 0.037336829839121406, 0.03712315965686395, 0.03690223969942172, 0.03667421422928117, 0.036439231512109274, 0.03619744365631504, 0.03594900644922451, 0.03569407919011589, 0.035432824520364815, 0.03516540825095256, 0.034891999187592754, 0.03461276895373386, 0.034327891811696175, 0.03403754448220348, 0.03374190596256939, 0.03344115734379898, 0.03313548162686572, 0.032825063538422565, 0.032510089346205105, 0.03219074667438249, 0.03186722431910982, 0.031539712064532675, 0.03120840049949164, 0.030873480835170858, 0.03053514472393069, 0.0301935840795603, 0.029848990899181048, 0.02950155708702655, 0.029151474280319688, 0.028798933677461093, 0.028444125868737388, 0.028087240669751014, 0.027728466957766755, 0.027367992511163026, 0.027006003852168566, 0.026642686093057866, 0.026278222785970744, 0.025912795776513554, 0.025546585061291437, 0.02517976864951269, 0.02481252242879783, 0.024445020035317504, 0.02407743272837456, 0.023709929269536956, 0.02334267580641931, 0.022975835761202032, 0.022609569723968055, 0.02224403535092835, 0.021879387267598385, 0.021515776976978884, 0.021153352772785516, 0.020792259657763056, 0.02043263926711133, 0.020074629797041145, 0.019718365938470435, 0.019363978815862017, 0.019011595931196563, 0.018661341113065943, 0.018313334470864574, 0.017967692354048354, 0.017624527316423555, 0.017283948085420497, 0.016946059536299903, 0.016610962671232896, 0.01627875460318899, 0.0159495285445601, 0.015623373800442372, 0.015300375766491934, 0.014980615931264925, 0.014664171882946955, 0.0143511173203721, 0.014041522068226746, 0.013735452096329218, 0.013432969542871884, 0.013134132741508665, 0.01283899625216716, 0.0125476108954615, 0.012260023790578905, 0.01197627839651037, 0.011696414556493402, 0.011420468545532764, 0.011148473120863266, 0.010880457575217196, 0.01061644779275778, 0.010356466307539038, 0.010100532364351792, 0.009848661981815167, 0.009600868017572787, 0.009357160235452985, 0.00911754537445276, 0.008882027219405753, 0.008650606673195494, 0.008423281830376106, 0.008200048052064144, 0.007980898041966587, 0.007765821923411856, 0.007554807317252622, 0.00734783942051125, 0.007144901085641026, 0.006945972900278813, 0.006751033267367329, 0.006560058485528049, 0.006373022829568614, 0.006189898631011701, 0.006010656358535378, 0.005835264698218323, 0.005663690633486606, 0.005495899524662148, 0.005331855188016576, 0.00517151997423776, 0.005014854846219947, 0.0048618194560922185, 0.004712372221403659, 0.004566470400387479, 0.004424070166230155, 0.004285126680275449, 0.004149594164097062, 0.004017425970377496, 0.0038885746525345525, 0.003762992033040712, 0.0036406292703844594, 0.0035214369246263713, 0.003405365021506527, 0.0032923631150635463, 0.003182380348729108, 0.00307536551486551, 0.002971267112717275, 0.002870033404751324, 0.002771612471363647, 0.0026759522639336585, 0.0025830006562107682, 0.002492705494020783, 0.0024050146432828654, 0.0023198760363307694, 0.0022372377165349403, 0.0021570478812249147, 0.002079254922914089, 0.002003807468831613, 0.0019306544187685899, 0.0018597449812482166, 0.001791028708031767, 0.001724455526974524, 0.0016599757732478479, 0.0015975402189455457, 0.0015371001010945887, 0.0014786071480919778, 0.0014220136045912449, 0.0013672722548636065, 0.0013143364446602654, 0.0012631601016036885, 0.0012136977541369505, 0.001165904549061379, 0.00111973626769378, 0.0010751493406754849, 0.0010321008614663071, 0.000990548598557279, 0.0009504510064366802, 0.000911767235344494, 0.0008744571398508864, 0.0008384812862947461, 0.0008038009591186315, 0.0007703781661367505, 0.0007381756427727404, 0.0007071568553041587, 0.0006772860031505917, 0.0006485280202422817, 0.000620848575506051, 0.0005942140725051567, 0.0005685916482694795, 0.0005439491713521765, 0.0005202552391485965, 0.0004974791745128755, 0.0004755910217072115, 0.000454561541718332, 0.0004343622069751615, 0.0004149651955011534],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.00011257974777361855, 0.0003060234826255299, 0.0007443793087479585, 0.0016202382839710565, 0.0031557932603104395, 0.005500260471221883, 0.008578335473875393, 0.011972031573897268, 0.014951258090714032, 0.016708316018054] + [0.016941994976895476] * 492 + [0.016708316018054, 0.014951258090714032, 0.011972031573897268, 0.008578335473875393, 0.005500260471221883, 0.0031557932603104395, 0.0016202382839710565, 0.0007443793087479585, 0.0003060234826255299, 0.00011257974777361855],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-6.989351536890887e-05, -0.00016999129667501453, -0.00036484513856434764, -0.000688248469168278, -0.0011342903610100825, -0.0016175167177644545, -0.0019621132850645186, -0.0019559640571875187, -0.0014656221003759447, -0.00054595354824654] + [0.0] * 492 + [0.00054595354824654, 0.0014656221003759447, 0.0019559640571875187, 0.0019621132850645186, 0.0016175167177644545, 0.0011342903610100825, 0.000688248469168278, 0.00036484513856434764, 0.00016999129667501453, 6.989351536890887e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [5.6381512762923065e-05, 0.0001532608416044855, 0.0003727955722642306, 0.0008114380010016118, 0.0015804654167561976, 0.002754607396893355, 0.004296150422876324, 0.005995760910205055, 0.00748779923151408, 0.008367758424127658] + [0.00848478811606515] * 492 + [0.008367758424127658, 0.00748779923151408, 0.005995760910205055, 0.004296150422876324, 0.002754607396893355, 0.0015804654167561976, 0.0008114380010016118, 0.0003727955722642306, 0.0001532608416044855, 5.6381512762923065e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-3.5003650361181064e-05, -8.513401968479211e-05, -0.0001827195498591853, -0.0003446844624887924, -0.0005680684823948154, -0.0008100750025685256, -0.0009826537846453576, -0.0009795741652920942, -0.0007340040530569791, -0.00027342117527499627] + [0.0] * 492 + [0.00027342117527499627, 0.0007340040530569791, 0.0009795741652920942, 0.0009826537846453576, 0.0008100750025685256, 0.0005680684823948154, 0.0003446844624887924, 0.0001827195498591853, 8.513401968479211e-05, 3.5003650361181064e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-5.6381512762923065e-05, -0.0001532608416044855, -0.0003727955722642306, -0.0008114380010016118, -0.0015804654167561976, -0.002754607396893355, -0.004296150422876324, -0.005995760910205055, -0.00748779923151408, -0.008367758424127658] + [-0.00848478811606515] * 492 + [-0.008367758424127658, -0.00748779923151408, -0.005995760910205055, -0.004296150422876324, -0.002754607396893355, -0.0015804654167561976, -0.0008114380010016118, -0.0003727955722642306, -0.0001532608416044855, -5.6381512762923065e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [3.5003650361181064e-05, 8.513401968479211e-05, 0.0001827195498591853, 0.0003446844624887924, 0.0005680684823948154, 0.0008100750025685256, 0.0009826537846453576, 0.0009795741652920942, 0.0007340040530569791, 0.00027342117527499627] + [0.0] * 492 + [-0.00027342117527499627, -0.0007340040530569791, -0.0009795741652920942, -0.0009826537846453576, -0.0008100750025685256, -0.0005680684823948154, -0.0003446844624887924, -0.0001827195498591853, -8.513401968479211e-05, -3.5003650361181064e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [6.99245477380325e-05, 0.00017006677195535174, 0.00036500712796999033, 0.0006885540480253618, 0.001134793980222687, 0.0016182348870478903, 0.001962984453489845, 0.001956832495386611, 0.0014662728292135848, 0.0005461959488747543] + [0.0] * 492 + [-0.0005461959488747543, -0.0014662728292135848, -0.001956832495386611, -0.001962984453489845, -0.0016182348870478903, -0.001134793980222687, -0.0006885540480253618, -0.00036500712796999033, -0.00017006677195535174, -6.99245477380325e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00011262973261513518, 0.000306159355511923, 0.0007447098094153684, 0.0016209576616161932, 0.0031571944166382464, 0.00550270255919411, 0.008582144211660099, 0.011977347095673498, 0.014957896374072433, 0.016715734426290724] + [0.016949517137414067] * 492 + [0.016715734426290724, 0.014957896374072433, 0.011977347095673498, 0.008582144211660099, 0.00550270255919411, 0.0031571944166382464, 0.0016209576616161932, 0.0007447098094153684, 0.000306159355511923, 0.00011262973261513518],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [3.494675768445444e-05, 8.499564833750727e-05, 0.00018242256928217382, 0.000344124234584139, 0.0005671451805050413, 0.0008087583588822272, 0.0009810566425322593, 0.0009779820285937594, 0.0007328110501879724, 0.00027297677412327] + [0.0] * 492 + [-0.00027297677412327, -0.0007328110501879724, -0.0009779820285937594, -0.0009810566425322593, -0.0008087583588822272, -0.0005671451805050413, -0.000344124234584139, -0.00018242256928217382, -8.499564833750727e-05, -3.494675768445444e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [5.628987388680927e-05, 0.00015301174131276496, 0.00037218965437397925, 0.0008101191419855282, 0.0015778966301552197, 0.0027501302356109417, 0.004289167736937697, 0.005986015786948634, 0.007475629045357016, 0.008354158009027] + [0.008470997488447738] * 492 + [0.008354158009027, 0.007475629045357016, 0.005986015786948634, 0.004289167736937697, 0.0027501302356109417, 0.0015778966301552197, 0.0008101191419855282, 0.00037218965437397925, 0.00015301174131276496, 5.628987388680927e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00038490806108277463, 0.0009361529472193725, 0.0020092255216962282, 0.0037902283554132428, 0.006246609592561508, 0.008907768057129978, 0.010805483401324121, 0.01077161920996389, 0.008071274680608118, 0.003006601121544322] + [0.0] * 492 + [-0.003006601121544322, -0.008071274680608118, -0.01077161920996389, -0.010805483401324121, -0.008907768057129978, -0.006246609592561508, -0.0037902283554132428, -0.0020092255216962282, -0.0009361529472193725, -0.00038490806108277463],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 492 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 492 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00038490806108277463, -0.0009361529472193725, -0.0020092255216962282, -0.0037902283554132428, -0.006246609592561508, -0.008907768057129978, -0.010805483401324121, -0.01077161920996389, -0.008071274680608118, -0.003006601121544322] + [0.0] * 492 + [0.003006601121544322, 0.008071274680608118, 0.01077161920996389, 0.010805483401324121, 0.008907768057129978, 0.006246609592561508, 0.0037902283554132428, 0.0020092255216962282, 0.0009361529472193725, 0.00038490806108277463],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-3.494675768445444e-05, -8.499564833750727e-05, -0.00018242256928217382, -0.000344124234584139, -0.0005671451805050413, -0.0008087583588822272, -0.0009810566425322593, -0.0009779820285937594, -0.0007328110501879724, -0.00027297677412327] + [0.0] * 492 + [0.00027297677412327, 0.0007328110501879724, 0.0009779820285937594, 0.0009810566425322593, 0.0008087583588822272, 0.0005671451805050413, 0.000344124234584139, 0.00018242256928217382, 8.499564833750727e-05, 3.494675768445444e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q7_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-5.628987388680927e-05, -0.00015301174131276496, -0.00037218965437397925, -0.0008101191419855282, -0.0015778966301552197, -0.0027501302356109417, -0.004289167736937697, -0.005986015786948634, -0.007475629045357016, -0.008354158009027] + [-0.008470997488447738] * 492 + [-0.008354158009027, -0.007475629045357016, -0.005986015786948634, -0.004289167736937697, -0.0027501302356109417, -0.0015778966301552197, -0.0008101191419855282, -0.00037218965437397925, -0.00015301174131276496, -5.628987388680927e-05],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 280 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_ro_wf": {
            "type": "arbitrary",
            "samples": [0.0004149651955011534, 0.0004343622069751615, 0.000454561541718332, 0.0004755910217072115, 0.0004974791745128755, 0.0005202552391485965, 0.0005439491713521765, 0.0005685916482694795, 0.0005942140725051567, 0.000620848575506051, 0.0006485280202422817, 0.0006772860031505917, 0.0007071568553041587, 0.0007381756427727404, 0.0007703781661367505, 0.0008038009591186315, 0.0008384812862947461, 0.0008744571398508864, 0.000911767235344494, 0.0009504510064366802, 0.000990548598557279, 0.0010321008614663071, 0.0010751493406754849, 0.00111973626769378, 0.001165904549061379, 0.0012136977541369505, 0.0012631601016036885, 0.0013143364446602654, 0.0013672722548636065, 0.0014220136045912449, 0.0014786071480919778, 0.0015371001010945887, 0.0015975402189455457, 0.0016599757732478479, 0.001724455526974524, 0.001791028708031767, 0.0018597449812482166, 0.0019306544187685899, 0.002003807468831613, 0.002079254922914089, 0.0021570478812249147, 0.0022372377165349403, 0.0023198760363307694, 0.0024050146432828654, 0.002492705494020783, 0.0025830006562107682, 0.0026759522639336585, 0.002771612471363647, 0.002870033404751324, 0.002971267112717275, 0.00307536551486551, 0.003182380348729108, 0.0032923631150635463, 0.003405365021506527, 0.0035214369246263713, 0.0036406292703844594, 0.003762992033040712, 0.0038885746525345525, 0.004017425970377496, 0.004149594164097062, 0.004285126680275449, 0.004424070166230155, 0.004566470400387479, 0.004712372221403659, 0.0048618194560922185, 0.005014854846219947, 0.00517151997423776, 0.005331855188016576, 0.005495899524662148, 0.005663690633486606, 0.005835264698218323, 0.006010656358535378, 0.006189898631011701, 0.006373022829568614, 0.006560058485528049, 0.006751033267367329, 0.006945972900278813, 0.007144901085641026, 0.00734783942051125, 0.007554807317252622, 0.007765821923411856, 0.007980898041966587, 0.008200048052064144, 0.008423281830376106, 0.008650606673195494, 0.008882027219405753, 0.00911754537445276, 0.009357160235452985, 0.009600868017572787, 0.009848661981815167, 0.010100532364351792, 0.010356466307539038, 0.01061644779275778, 0.010880457575217196, 0.011148473120863266, 0.011420468545532764, 0.011696414556493402, 0.01197627839651037, 0.012260023790578905, 0.0125476108954615, 0.01283899625216716, 0.013134132741508665, 0.013432969542871884, 0.013735452096329218, 0.014041522068226746, 0.0143511173203721, 0.014664171882946955, 0.014980615931264925, 0.015300375766491934, 0.015623373800442372, 0.0159495285445601, 0.01627875460318899, 0.016610962671232896, 0.016946059536299903, 0.017283948085420497, 0.017624527316423555, 0.017967692354048354, 0.018313334470864574, 0.018661341113065943, 0.019011595931196563, 0.019363978815862017, 0.019718365938470435, 0.020074629797041145, 0.02043263926711133, 0.020792259657763056, 0.021153352772785516, 0.021515776976978884, 0.021879387267598385, 0.02224403535092835, 0.022609569723968055, 0.022975835761202032, 0.02334267580641931, 0.023709929269536956, 0.02407743272837456, 0.024445020035317504, 0.02481252242879783, 0.02517976864951269, 0.025546585061291437, 0.025912795776513554, 0.026278222785970744, 0.026642686093057866, 0.027006003852168566, 0.027367992511163026, 0.027728466957766755, 0.028087240669751014, 0.028444125868737388, 0.028798933677461093, 0.029151474280319688, 0.02950155708702655, 0.029848990899181048, 0.0301935840795603, 0.03053514472393069, 0.030873480835170858, 0.03120840049949164, 0.031539712064532675, 0.03186722431910982, 0.03219074667438249, 0.032510089346205105, 0.032825063538422565, 0.03313548162686572, 0.03344115734379898, 0.03374190596256939, 0.03403754448220348, 0.034327891811696175, 0.03461276895373386, 0.034891999187592754, 0.03516540825095256, 0.035432824520364815, 0.03569407919011589, 0.03594900644922451, 0.03619744365631504, 0.036439231512109274, 0.03667421422928117, 0.03690223969942172, 0.03712315965686395, 0.037336829839121406, 0.03754311014369757, 0.03774186478102777, 0.037932962423320234, 0.038116276349067994, 0.038291684583009286, 0.03845907003132011, 0.03861832061182935, 0.03876932937905377, 0.03891199464385774, 0.039046220087550265, 0.03917191487024018, 0.03928899373327889, 0.03939737709562892, 0.03949699114400586, 0.03958776791665071, 0.03966964538059961, 0.039742567502327894, 0.03980648431165596, 0.039861351958814774, 0.039907132764579925, 0.03994379526339395, 0.039971314239407744, 0.03998967075538343, 0.03999885217441219] + [0.04000000000000001] * 1600 + [0.03999885217441219, 0.03998967075538343, 0.039971314239407744, 0.03994379526339395, 0.039907132764579925, 0.039861351958814774, 0.03980648431165596, 0.039742567502327894, 0.03966964538059961, 0.03958776791665071, 0.03949699114400586, 0.03939737709562892, 0.03928899373327889, 0.03917191487024018, 0.039046220087550265, 0.03891199464385774, 0.03876932937905377, 0.03861832061182935, 0.03845907003132011, 0.038291684583009286, 0.038116276349067994, 0.037932962423320234, 0.03774186478102777, 0.03754311014369757, 0.037336829839121406, 0.03712315965686395, 0.03690223969942172, 0.03667421422928117, 0.036439231512109274, 0.03619744365631504, 0.03594900644922451, 0.03569407919011589, 0.035432824520364815, 0.03516540825095256, 0.034891999187592754, 0.03461276895373386, 0.034327891811696175, 0.03403754448220348, 0.03374190596256939, 0.03344115734379898, 0.03313548162686572, 0.032825063538422565, 0.032510089346205105, 0.03219074667438249, 0.03186722431910982, 0.031539712064532675, 0.03120840049949164, 0.030873480835170858, 0.03053514472393069, 0.0301935840795603, 0.029848990899181048, 0.02950155708702655, 0.029151474280319688, 0.028798933677461093, 0.028444125868737388, 0.028087240669751014, 0.027728466957766755, 0.027367992511163026, 0.027006003852168566, 0.026642686093057866, 0.026278222785970744, 0.025912795776513554, 0.025546585061291437, 0.02517976864951269, 0.02481252242879783, 0.024445020035317504, 0.02407743272837456, 0.023709929269536956, 0.02334267580641931, 0.022975835761202032, 0.022609569723968055, 0.02224403535092835, 0.021879387267598385, 0.021515776976978884, 0.021153352772785516, 0.020792259657763056, 0.02043263926711133, 0.020074629797041145, 0.019718365938470435, 0.019363978815862017, 0.019011595931196563, 0.018661341113065943, 0.018313334470864574, 0.017967692354048354, 0.017624527316423555, 0.017283948085420497, 0.016946059536299903, 0.016610962671232896, 0.01627875460318899, 0.0159495285445601, 0.015623373800442372, 0.015300375766491934, 0.014980615931264925, 0.014664171882946955, 0.0143511173203721, 0.014041522068226746, 0.013735452096329218, 0.013432969542871884, 0.013134132741508665, 0.01283899625216716, 0.0125476108954615, 0.012260023790578905, 0.01197627839651037, 0.011696414556493402, 0.011420468545532764, 0.011148473120863266, 0.010880457575217196, 0.01061644779275778, 0.010356466307539038, 0.010100532364351792, 0.009848661981815167, 0.009600868017572787, 0.009357160235452985, 0.00911754537445276, 0.008882027219405753, 0.008650606673195494, 0.008423281830376106, 0.008200048052064144, 0.007980898041966587, 0.007765821923411856, 0.007554807317252622, 0.00734783942051125, 0.007144901085641026, 0.006945972900278813, 0.006751033267367329, 0.006560058485528049, 0.006373022829568614, 0.006189898631011701, 0.006010656358535378, 0.005835264698218323, 0.005663690633486606, 0.005495899524662148, 0.005331855188016576, 0.00517151997423776, 0.005014854846219947, 0.0048618194560922185, 0.004712372221403659, 0.004566470400387479, 0.004424070166230155, 0.004285126680275449, 0.004149594164097062, 0.004017425970377496, 0.0038885746525345525, 0.003762992033040712, 0.0036406292703844594, 0.0035214369246263713, 0.003405365021506527, 0.0032923631150635463, 0.003182380348729108, 0.00307536551486551, 0.002971267112717275, 0.002870033404751324, 0.002771612471363647, 0.0026759522639336585, 0.0025830006562107682, 0.002492705494020783, 0.0024050146432828654, 0.0023198760363307694, 0.0022372377165349403, 0.0021570478812249147, 0.002079254922914089, 0.002003807468831613, 0.0019306544187685899, 0.0018597449812482166, 0.001791028708031767, 0.001724455526974524, 0.0016599757732478479, 0.0015975402189455457, 0.0015371001010945887, 0.0014786071480919778, 0.0014220136045912449, 0.0013672722548636065, 0.0013143364446602654, 0.0012631601016036885, 0.0012136977541369505, 0.001165904549061379, 0.00111973626769378, 0.0010751493406754849, 0.0010321008614663071, 0.000990548598557279, 0.0009504510064366802, 0.000911767235344494, 0.0008744571398508864, 0.0008384812862947461, 0.0008038009591186315, 0.0007703781661367505, 0.0007381756427727404, 0.0007071568553041587, 0.0006772860031505917, 0.0006485280202422817, 0.000620848575506051, 0.0005942140725051567, 0.0005685916482694795, 0.0005439491713521765, 0.0005202552391485965, 0.0004974791745128755, 0.0004755910217072115, 0.000454561541718332, 0.0004343622069751615, 0.0004149651955011534],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X180_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0006060349618751102, -0.0014739660532995628, -0.003163511070706866, -0.005967687167707441, -0.009835241682461419, -0.014025216462624716, -0.01701315556432408, -0.01695983663963802, -0.012708163683519139, -0.004733871748341827] + [0.0] * 280 + [0.004733871748341827, 0.012708163683519139, 0.01695983663963802, 0.01701315556432408, 0.014025216462624716, 0.009835241682461419, 0.005967687167707441, 0.003163511070706866, 0.0014739660532995628, 0.0006060349618751102],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00027510759179523057, -0.0006691020763167246, -0.0014360655193669622, -0.0027090121009117987, -0.004464675842486502, -0.006366701210605477, -0.00772306640801254, -0.007698862456276641, -0.005768829402672357, -0.002148925620601698] + [0.0] * 280 + [0.002148925620601698, 0.005768829402672357, 0.007698862456276641, 0.00772306640801254, 0.006366701210605477, 0.004464675842486502, 0.0027090121009117987, 0.0014360655193669622, 0.0006691020763167246, 0.00027510759179523057],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mX90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00027510759179523057, 0.0006691020763167246, 0.0014360655193669622, 0.0027090121009117987, 0.004464675842486502, 0.006366701210605477, 0.00772306640801254, 0.007698862456276641, 0.005768829402672357, 0.002148925620601698] + [0.0] * 280 + [-0.002148925620601698, -0.005768829402672357, -0.007698862456276641, -0.00772306640801254, -0.006366701210605477, -0.004464675842486502, -0.0027090121009117987, -0.0014360655193669622, -0.0006691020763167246, -0.00027510759179523057],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006060349618751102, 0.0014739660532995628, 0.003163511070706866, 0.005967687167707441, 0.009835241682461419, 0.014025216462624716, 0.01701315556432408, 0.01695983663963802, 0.012708163683519139, 0.004733871748341827] + [0.0] * 280 + [-0.004733871748341827, -0.012708163683519139, -0.01695983663963802, -0.01701315556432408, -0.014025216462624716, -0.009835241682461419, -0.005967687167707441, -0.003163511070706866, -0.0014739660532995628, -0.0006060349618751102],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 280 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00027510759179523057, 0.0006691020763167246, 0.0014360655193669622, 0.0027090121009117987, 0.004464675842486502, 0.006366701210605477, 0.00772306640801254, 0.007698862456276641, 0.005768829402672357, 0.002148925620601698] + [0.0] * 280 + [-0.002148925620601698, -0.005768829402672357, -0.007698862456276641, -0.00772306640801254, -0.006366701210605477, -0.004464675842486502, -0.0027090121009117987, -0.0014360655193669622, -0.0006691020763167246, -0.00027510759179523057],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 280 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y360_I_wf": {
            "type": "arbitrary",
            "samples": [0.00038490806108277463, 0.0009361529472193725, 0.0020092255216962282, 0.0037902283554132428, 0.006246609592561508, 0.008907768057129978, 0.010805483401324121, 0.01077161920996389, 0.008071274680608118, 0.003006601121544322] + [0.0] * 280 + [-0.003006601121544322, -0.008071274680608118, -0.01077161920996389, -0.010805483401324121, -0.008907768057129978, -0.006246609592561508, -0.0037902283554132428, -0.0020092255216962282, -0.0009361529472193725, -0.00038490806108277463],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_Y360_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 280 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_X360_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00038490806108277463, -0.0009361529472193725, -0.0020092255216962282, -0.0037902283554132428, -0.006246609592561508, -0.008907768057129978, -0.010805483401324121, -0.01077161920996389, -0.008071274680608118, -0.003006601121544322] + [0.0] * 280 + [0.003006601121544322, 0.008071274680608118, 0.01077161920996389, 0.010805483401324121, 0.008907768057129978, 0.006246609592561508, 0.0037902283554132428, 0.0020092255216962282, 0.0009361529472193725, 0.00038490806108277463],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mY90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00027510759179523057, -0.0006691020763167246, -0.0014360655193669622, -0.0027090121009117987, -0.004464675842486502, -0.006366701210605477, -0.00772306640801254, -0.007698862456276641, -0.005768829402672357, -0.002148925620601698] + [0.0] * 280 + [0.002148925620601698, 0.005768829402672357, 0.007698862456276641, 0.00772306640801254, 0.006366701210605477, 0.004464675842486502, 0.0027090121009117987, 0.0014360655193669622, 0.0006691020763167246, 0.00027510759179523057],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q8_d_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 280 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "rise_wf": {
            "type": "arbitrary",
            "samples": [0.0032754804057496334, 0.005968314427627137, 0.010448563941567294, 0.01757477344936297, 0.028402141495854794, 0.04410021012179409, 0.06578978263086196, 0.09429843062234541, 0.1298609869433399, 0.17182294328429568, 0.21842977065588376, 0.26679072434338974, 0.3130818152967473, 0.3529987610338382, 0.38239899273324, 0.39800499167707293],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "fall_wf": {
            "type": "arbitrary",
            "samples": [0.39800499167707293, 0.38239899273324, 0.3529987610338382, 0.3130818152967473, 0.26679072434338974, 0.21842977065588376, 0.17182294328429568, 0.1298609869433399, 0.09429843062234541, 0.06578978263086196, 0.04410021012179409, 0.028402141495854794, 0.01757477344936297, 0.010448563941567294, 0.005968314427627137, 0.0032754804057496334],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0008247924959848904, 0.0022420184540851078, 0.005453542756698274, 0.011870344398123803, 0.02312027386326841, 0.04029653336716045, 0.06284742031151912, 0.08771064067136396, 0.10953733440184583, 0.12241005993321687] + [0.12412206103051526] * 32 + [0.12241005993321687, 0.10953733440184583, 0.08771064067136396, 0.06284742031151912, 0.04029653336716045, 0.02312027386326841, 0.011870344398123803, 0.005453542756698274, 0.0022420184540851078, 0.0008247924959848904],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003685439935695536, 0.0010018064407078446, 0.002436819486646631, 0.005304054232824478, 0.01033088698487238, 0.018005795889799343, 0.028082262362842645, 0.03919195427811065, 0.04894482777418412, 0.054696778353937145] + [0.05546175587793897] * 32 + [0.054696778353937145, 0.04894482777418412, 0.03919195427811065, 0.028082262362842645, 0.018005795889799343, 0.01033088698487238, 0.005304054232824478, 0.002436819486646631, 0.0010018064407078446, 0.0003685439935695536],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003685439935695536, -0.0010018064407078446, -0.002436819486646631, -0.005304054232824478, -0.01033088698487238, -0.018005795889799343, -0.028082262362842645, -0.03919195427811065, -0.04894482777418412, -0.054696778353937145] + [-0.05546175587793897] * 32 + [-0.054696778353937145, -0.04894482777418412, -0.03919195427811065, -0.028082262362842645, -0.018005795889799343, -0.01033088698487238, -0.005304054232824478, -0.002436819486646631, -0.0010018064407078446, -0.0003685439935695536],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0008247924959848904, 0.0022420184540851078, 0.005453542756698274, 0.011870344398123803, 0.02312027386326841, 0.04029653336716045, 0.06284742031151912, 0.08771064067136396, 0.10953733440184583, 0.12241005993321687] + [0.12412206103051526] * 32 + [0.12241005993321687, 0.10953733440184583, 0.08771064067136396, 0.06284742031151912, 0.04029653336716045, 0.02312027386326841, 0.011870344398123803, 0.005453542756698274, 0.0022420184540851078, 0.0008247924959848904],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003685439935695536, 0.0010018064407078446, 0.002436819486646631, 0.005304054232824478, 0.01033088698487238, 0.018005795889799343, 0.028082262362842645, 0.03919195427811065, 0.04894482777418412, 0.054696778353937145] + [0.05546175587793897] * 32 + [0.054696778353937145, 0.04894482777418412, 0.03919195427811065, 0.028082262362842645, 0.018005795889799343, 0.01033088698487238, 0.005304054232824478, 0.002436819486646631, 0.0010018064407078446, 0.0003685439935695536],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_1_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0003685439935695536, -0.0010018064407078446, -0.002436819486646631, -0.005304054232824478, -0.01033088698487238, -0.018005795889799343, -0.028082262362842645, -0.03919195427811065, -0.04894482777418412, -0.054696778353937145] + [-0.05546175587793897] * 32 + [-0.054696778353937145, -0.04894482777418412, -0.03919195427811065, -0.028082262362842645, -0.018005795889799343, -0.01033088698487238, -0.005304054232824478, -0.002436819486646631, -0.0010018064407078446, -0.0003685439935695536],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0011846004105641446, 0.003220077770021639, 0.007832599132585027, 0.01704866971511929, 0.03320627435883577, 0.05787551439110632, 0.09026401218044879, 0.12597357693715647, 0.15732195908206426, 0.17581028920603403] + [0.17826913456728366] * 32 + [0.17581028920603403, 0.15732195908206426, 0.12597357693715647, 0.09026401218044879, 0.05787551439110632, 0.03320627435883577, 0.01704866971511929, 0.007832599132585027, 0.003220077770021639, 0.0011846004105641446],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0003368503543574758, 0.0009156541971599167, 0.0022272605764966998, 0.004847922036534303, 0.009442462778936971, 0.016457353346670735, 0.025667274987885267, 0.03582156789119409, 0.04473572454678471, 0.049993025235015386] + [0.05069221706701275] * 32 + [0.049993025235015386, 0.04473572454678471, 0.03582156789119409, 0.025667274987885267, 0.016457353346670735, 0.009442462778936971, 0.004847922036534303, 0.0022272605764966998, 0.0009156541971599167, 0.0003368503543574758],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0003368503543574758, -0.0009156541971599167, -0.0022272605764966998, -0.004847922036534303, -0.009442462778936971, -0.016457353346670735, -0.025667274987885267, -0.03582156789119409, -0.04473572454678471, -0.049993025235015386] + [-0.05069221706701275] * 32 + [-0.049993025235015386, -0.04473572454678471, -0.03582156789119409, -0.025667274987885267, -0.016457353346670735, -0.009442462778936971, -0.004847922036534303, -0.0022272605764966998, -0.0009156541971599167, -0.0003368503543574758],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0011846004105641446, 0.003220077770021639, 0.007832599132585027, 0.01704866971511929, 0.03320627435883577, 0.05787551439110632, 0.09026401218044879, 0.12597357693715647, 0.15732195908206426, 0.17581028920603403] + [0.17826913456728366] * 32 + [0.17581028920603403, 0.15732195908206426, 0.12597357693715647, 0.09026401218044879, 0.05787551439110632, 0.03320627435883577, 0.01704866971511929, 0.007832599132585027, 0.003220077770021639, 0.0011846004105641446],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0003368503543574758, 0.0009156541971599167, 0.0022272605764966998, 0.004847922036534303, 0.009442462778936971, 0.016457353346670735, 0.025667274987885267, 0.03582156789119409, 0.04473572454678471, 0.049993025235015386] + [0.05069221706701275] * 32 + [0.049993025235015386, 0.04473572454678471, 0.03582156789119409, 0.025667274987885267, 0.016457353346670735, 0.009442462778936971, 0.004847922036534303, 0.0022272605764966998, 0.0009156541971599167, 0.0003368503543574758],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_2_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0003368503543574758, -0.0009156541971599167, -0.0022272605764966998, -0.004847922036534303, -0.009442462778936971, -0.016457353346670735, -0.025667274987885267, -0.03582156789119409, -0.04473572454678471, -0.049993025235015386] + [-0.05069221706701275] * 32 + [-0.049993025235015386, -0.04473572454678471, -0.03582156789119409, -0.025667274987885267, -0.016457353346670735, -0.009442462778936971, -0.004847922036534303, -0.0022272605764966998, -0.0009156541971599167, -0.0003368503543574758],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006342512019745167, 0.0017240735170056364, 0.004193680307826982, 0.009128090082065216, 0.017779091782651992, 0.030987339055514325, 0.04832858211928844, 0.06744796969247237, 0.08423232066690386, 0.09413122454964444] + [0.09544772386193097] * 32 + [0.09413122454964444, 0.08423232066690386, 0.06744796969247237, 0.04832858211928844, 0.030987339055514325, 0.017779091782651992, 0.009128090082065216, 0.004193680307826982, 0.0017240735170056364, 0.0006342512019745167],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00032851703240092234, 0.0008930018795147186, 0.002172160502457921, 0.004727989566141715, 0.009208866223725546, 0.016050215808542965, 0.02503229371666342, 0.03493538013937992, 0.043629009975208445, 0.04875625059762442] + [0.04943814516224458] * 32 + [0.04875625059762442, 0.043629009975208445, 0.03493538013937992, 0.02503229371666342, 0.016050215808542965, 0.009208866223725546, 0.004727989566141715, 0.002172160502457921, 0.0008930018795147186, 0.00032851703240092234],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00032851703240092234, -0.0008930018795147186, -0.002172160502457921, -0.004727989566141715, -0.009208866223725546, -0.016050215808542965, -0.02503229371666342, -0.03493538013937992, -0.043629009975208445, -0.04875625059762442] + [-0.04943814516224458] * 32 + [-0.04875625059762442, -0.043629009975208445, -0.03493538013937992, -0.02503229371666342, -0.016050215808542965, -0.009208866223725546, -0.004727989566141715, -0.002172160502457921, -0.0008930018795147186, -0.00032851703240092234],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0006342512019745167, 0.0017240735170056364, 0.004193680307826982, 0.009128090082065216, 0.017779091782651992, 0.030987339055514325, 0.04832858211928844, 0.06744796969247237, 0.08423232066690386, 0.09413122454964444] + [0.09544772386193097] * 32 + [0.09413122454964444, 0.08423232066690386, 0.06744796969247237, 0.04832858211928844, 0.030987339055514325, 0.017779091782651992, 0.009128090082065216, 0.004193680307826982, 0.0017240735170056364, 0.0006342512019745167],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00032851703240092234, 0.0008930018795147186, 0.002172160502457921, 0.004727989566141715, 0.009208866223725546, 0.016050215808542965, 0.02503229371666342, 0.03493538013937992, 0.043629009975208445, 0.04875625059762442] + [0.04943814516224458] * 32 + [0.04875625059762442, 0.043629009975208445, 0.03493538013937992, 0.02503229371666342, 0.016050215808542965, 0.009208866223725546, 0.004727989566141715, 0.002172160502457921, 0.0008930018795147186, 0.00032851703240092234],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_3_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00032851703240092234, -0.0008930018795147186, -0.002172160502457921, -0.004727989566141715, -0.009208866223725546, -0.016050215808542965, -0.02503229371666342, -0.03493538013937992, -0.043629009975208445, -0.04875625059762442] + [-0.04943814516224458] * 32 + [-0.04875625059762442, -0.043629009975208445, -0.03493538013937992, -0.02503229371666342, -0.016050215808542965, -0.009208866223725546, -0.004727989566141715, -0.002172160502457921, -0.0008930018795147186, -0.00032851703240092234],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044079793703683873, 0.001198213022269473, 0.0029145638550266725, 0.00634392692474935, 0.012356282425297615, 0.02153587582870766, 0.033587857983994364, 0.04687563193448955, 0.058540579925126415, 0.06542021436153592] + [0.0663351675837919] * 32 + [0.06542021436153592, 0.058540579925126415, 0.04687563193448955, 0.033587857983994364, 0.02153587582870766, 0.012356282425297615, 0.00634392692474935, 0.0029145638550266725, 0.001198213022269473, 0.00044079793703683873],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00022595032861955896, 0.0006141966724208969, 0.0014939876199350922, 0.0032518581711642393, 0.006333754856658392, 0.011039158334808279, 0.01721693073276873, 0.024028162452498593, 0.03000754350299156, 0.03353400207069409] + [0.03400300150075038] * 32 + [0.03353400207069409, 0.03000754350299156, 0.024028162452498593, 0.01721693073276873, 0.011039158334808279, 0.006333754856658392, 0.0032518581711642393, 0.0014939876199350922, 0.0006141966724208969, 0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00022595032861955896, -0.0006141966724208969, -0.0014939876199350922, -0.0032518581711642393, -0.006333754856658392, -0.011039158334808279, -0.01721693073276873, -0.024028162452498593, -0.03000754350299156, -0.03353400207069409] + [-0.03400300150075038] * 32 + [-0.03353400207069409, -0.03000754350299156, -0.024028162452498593, -0.01721693073276873, -0.011039158334808279, -0.006333754856658392, -0.0032518581711642393, -0.0014939876199350922, -0.0006141966724208969, -0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044079793703683873, 0.001198213022269473, 0.0029145638550266725, 0.00634392692474935, 0.012356282425297615, 0.02153587582870766, 0.033587857983994364, 0.04687563193448955, 0.058540579925126415, 0.06542021436153592] + [0.0663351675837919] * 32 + [0.06542021436153592, 0.058540579925126415, 0.04687563193448955, 0.033587857983994364, 0.02153587582870766, 0.012356282425297615, 0.00634392692474935, 0.0029145638550266725, 0.001198213022269473, 0.00044079793703683873],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00022595032861955896, 0.0006141966724208969, 0.0014939876199350922, 0.0032518581711642393, 0.006333754856658392, 0.011039158334808279, 0.01721693073276873, 0.024028162452498593, 0.03000754350299156, 0.03353400207069409] + [0.03400300150075038] * 32 + [0.03353400207069409, 0.03000754350299156, 0.024028162452498593, 0.01721693073276873, 0.011039158334808279, 0.006333754856658392, 0.0032518581711642393, 0.0014939876199350922, 0.0006141966724208969, 0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_4_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00022595032861955896, -0.0006141966724208969, -0.0014939876199350922, -0.0032518581711642393, -0.006333754856658392, -0.011039158334808279, -0.01721693073276873, -0.024028162452498593, -0.03000754350299156, -0.03353400207069409] + [-0.03400300150075038] * 32 + [-0.03353400207069409, -0.03000754350299156, -0.024028162452498593, -0.01721693073276873, -0.011039158334808279, -0.006333754856658392, -0.0032518581711642393, -0.0014939876199350922, -0.0006141966724208969, -0.00022595032861955896],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005376176462019842, 0.0014613962783297776, 0.003554737506209946, 0.0077373480554109395, 0.015070296195012088, 0.02626615485035813, 0.04096531229639685, 0.05717169883838341, 0.07139881143321992, 0.07978953326212786] + [0.08090545272636318] * 32 + [0.07978953326212786, 0.07139881143321992, 0.05717169883838341, 0.04096531229639685, 0.02626615485035813, 0.015070296195012088, 0.0077373480554109395, 0.003554737506209946, 0.0014613962783297776, 0.0005376176462019842],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002308102618338501, 0.0006274073405648289, 0.0015261215853965336, 0.003321801922212349, 0.006469986681533849, 0.01127659800828397, 0.0175872472267855, 0.024544980752762718, 0.03065297145275578, 0.034255280112054566] + [0.0347343671835918] * 32 + [0.034255280112054566, 0.03065297145275578, 0.024544980752762718, 0.0175872472267855, 0.01127659800828397, 0.006469986681533849, 0.003321801922212349, 0.0015261215853965336, 0.0006274073405648289, 0.0002308102618338501],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002623693252915482, 0.0007131937692850755, 0.0017347906782480568, 0.003775997315537051, 0.007354638510402588, 0.012818465641476843, 0.019991980217712455, 0.02790105599391481, 0.03484420222195312, 0.03893906041813023] + [0.03948365384615385] * 32 + [0.03893906041813023, 0.03484420222195312, 0.02790105599391481, 0.019991980217712455, 0.012818465641476843, 0.007354638510402588, 0.003775997315537051, 0.0017347906782480568, 0.0007131937692850755, 0.0002623693252915482],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002623693252915482, -0.0007131937692850755, -0.0017347906782480568, -0.003775997315537051, -0.007354638510402588, -0.012818465641476843, -0.019991980217712455, -0.02790105599391481, -0.03484420222195312, -0.03893906041813023] + [-0.03948365384615385] * 32 + [-0.03893906041813023, -0.03484420222195312, -0.02790105599391481, -0.019991980217712455, -0.012818465641476843, -0.007354638510402588, -0.003775997315537051, -0.0017347906782480568, -0.0007131937692850755, -0.0002623693252915482],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005376176462019842, 0.0014613962783297776, 0.003554737506209946, 0.0077373480554109395, 0.015070296195012088, 0.02626615485035813, 0.04096531229639685, 0.05717169883838341, 0.07139881143321992, 0.07978953326212786] + [0.08090545272636318] * 32 + [0.07978953326212786, 0.07139881143321992, 0.05717169883838341, 0.04096531229639685, 0.02626615485035813, 0.015070296195012088, 0.0077373480554109395, 0.003554737506209946, 0.0014613962783297776, 0.0005376176462019842],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002623693252915482, 0.0007131937692850755, 0.0017347906782480568, 0.003775997315537051, 0.007354638510402588, 0.012818465641476843, 0.019991980217712455, 0.02790105599391481, 0.03484420222195312, 0.03893906041813023] + [0.03948365384615385] * 32 + [0.03893906041813023, 0.03484420222195312, 0.02790105599391481, 0.019991980217712455, 0.012818465641476843, 0.007354638510402588, 0.003775997315537051, 0.0017347906782480568, 0.0007131937692850755, 0.0002623693252915482],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_5_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002623693252915482, -0.0007131937692850755, -0.0017347906782480568, -0.003775997315537051, -0.007354638510402588, -0.012818465641476843, -0.019991980217712455, -0.02790105599391481, -0.03484420222195312, -0.03893906041813023] + [-0.03948365384615385] * 32 + [-0.03893906041813023, -0.03484420222195312, -0.02790105599391481, -0.019991980217712455, -0.012818465641476843, -0.007354638510402588, -0.003775997315537051, -0.0017347906782480568, -0.0007131937692850755, -0.0002623693252915482],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 84 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005184504950982889, 0.0014092945597812742, 0.003428003959800458, 0.007461496024943498, 0.0145330098049766, 0.025329713566321993, 0.03950481646568502, 0.05513341271025556, 0.06885330010740563, 0.076944875815832] + [0.07802101050525263] * 84 + [0.076944875815832, 0.06885330010740563, 0.05513341271025556, 0.03950481646568502, 0.025329713566321993, 0.0145330098049766, 0.007461496024943498, 0.003428003959800458, 0.0014092945597812742, 0.0005184504950982889],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0002329443775134499, 0.0006332084684365146, 0.001540232396495197, 0.0033525159360104934, 0.006529809411745918, 0.011380863583093407, 0.017749862267249776, 0.024771928323740536, 0.030936394670094108, 0.03457201096195432] + [0.03505552776388195] * 84 + [0.03457201096195432, 0.030936394670094108, 0.024771928323740536, 0.017749862267249776, 0.011380863583093407, 0.006529809411745918, 0.0033525159360104934, 0.001540232396495197, 0.0006332084684365146, 0.0002329443775134499],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0002329443775134499, -0.0006332084684365146, -0.001540232396495197, -0.0033525159360104934, -0.006529809411745918, -0.011380863583093407, -0.017749862267249776, -0.024771928323740536, -0.030936394670094108, -0.03457201096195432] + [-0.03505552776388195] * 84 + [-0.03457201096195432, -0.030936394670094108, -0.024771928323740536, -0.017749862267249776, -0.011380863583093407, -0.006529809411745918, -0.0033525159360104934, -0.001540232396495197, -0.0006332084684365146, -0.0002329443775134499],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005184504950982889, 0.0014092945597812742, 0.003428003959800458, 0.007461496024943498, 0.0145330098049766, 0.025329713566321993, 0.03950481646568502, 0.05513341271025556, 0.06885330010740563, 0.076944875815832] + [0.07802101050525263] * 84 + [0.076944875815832, 0.06885330010740563, 0.05513341271025556, 0.03950481646568502, 0.025329713566321993, 0.0145330098049766, 0.007461496024943498, 0.003428003959800458, 0.0014092945597812742, 0.0005184504950982889],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0002329443775134499, 0.0006332084684365146, 0.001540232396495197, 0.0033525159360104934, 0.006529809411745918, 0.011380863583093407, 0.017749862267249776, 0.024771928323740536, 0.030936394670094108, 0.03457201096195432] + [0.03505552776388195] * 84 + [0.03457201096195432, 0.030936394670094108, 0.024771928323740536, 0.017749862267249776, 0.011380863583093407, 0.006529809411745918, 0.0033525159360104934, 0.001540232396495197, 0.0006332084684365146, 0.0002329443775134499],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_6_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0002329443775134499, -0.0006332084684365146, -0.001540232396495197, -0.0033525159360104934, -0.006529809411745918, -0.011380863583093407, -0.017749862267249776, -0.024771928323740536, -0.030936394670094108, -0.03457201096195432] + [-0.03505552776388195] * 84 + [-0.03457201096195432, -0.030936394670094108, -0.024771928323740536, -0.017749862267249776, -0.011380863583093407, -0.006529809411745918, -0.0033525159360104934, -0.001540232396495197, -0.0006332084684365146, -0.0002329443775134499],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 84 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0004627241473524776, 0.0012578146413374455, 0.0030595403503643386, 0.006659487103896635, 0.012970909728224093, 0.022607115285784032, 0.035258588212814204, 0.049207323800797446, 0.061452510675225454, 0.06867435250162739] + [0.06963481740870435] * 84 + [0.06867435250162739, 0.061452510675225454, 0.049207323800797446, 0.035258588212814204, 0.022607115285784032, 0.012970909728224093, 0.006659487103896635, 0.0030595403503643386, 0.0012578146413374455, 0.0004627241473524776],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 84 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 84 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 84 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0004627241473524776, 0.0012578146413374455, 0.0030595403503643386, 0.006659487103896635, 0.012970909728224093, 0.022607115285784032, 0.035258588212814204, 0.049207323800797446, 0.061452510675225454, 0.06867435250162739] + [0.06963481740870435] * 84 + [0.06867435250162739, 0.061452510675225454, 0.049207323800797446, 0.035258588212814204, 0.022607115285784032, 0.012970909728224093, 0.006659487103896635, 0.0030595403503643386, 0.0012578146413374455, 0.0004627241473524776],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0005964190784955906, 0.0016212351432208527, 0.003943533629755371, 0.00858361333525516, 0.016718595888327338, 0.029138991218282048, 0.04544585540059031, 0.0634248004657296, 0.0792079903282838, 0.08851643958857824] + [0.08975441171102691] * 84 + [0.08851643958857824, 0.0792079903282838, 0.0634248004657296, 0.04544585540059031, 0.029138991218282048, 0.016718595888327338, 0.00858361333525516, 0.003943533629755371, 0.0016212351432208527, 0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_7_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.0005964190784955906, -0.0016212351432208527, -0.003943533629755371, -0.00858361333525516, -0.016718595888327338, -0.029138991218282048, -0.04544585540059031, -0.0634248004657296, -0.0792079903282838, -0.08851643958857824] + [-0.08975441171102691] * 84 + [-0.08851643958857824, -0.0792079903282838, -0.0634248004657296, -0.04544585540059031, -0.029138991218282048, -0.016718595888327338, -0.00858361333525516, -0.003943533629755371, -0.0016212351432208527, -0.0005964190784955906],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_grft_I_wf": {
            "type": "arbitrary",
            "samples": [0.00265800451309656, 0.0072252053679125105, 0.01757477344936297, 0.038253777933015445, 0.07450818547908036, 0.1298609869433399, 0.20253424665924025, 0.2826593111430865, 0.3529987610338382, 0.3944828466975665] + [0.4] * 32 + [0.3944828466975665, 0.3529987610338382, 0.2826593111430865, 0.20253424665924025, 0.1298609869433399, 0.07450818547908036, 0.038253777933015445, 0.01757477344936297, 0.0072252053679125105, 0.00265800451309656],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_X180_I_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 32 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_X360_I_wf": {
            "type": "arbitrary",
            "samples": [0.0006199838740978153, 0.001685290898897732, 0.004099344480357415, 0.008922755896361738, 0.017379155399365083, 0.03029028633420265, 0.047241442316060006, 0.06593074387528111, 0.08233753492108442, 0.09201376534751093] + [0.09330065032516259] * 32 + [0.09201376534751093, 0.08233753492108442, 0.06593074387528111, 0.047241442316060006, 0.03029028633420265, 0.017379155399365083, 0.008922755896361738, 0.004099344480357415, 0.001685290898897732, 0.0006199838740978153],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_X90_I_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 32 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_mX90_I_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 32 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_Y180_Q_wf": {
            "type": "arbitrary",
            "samples": [0.0009761601314482508, 0.002653478346981973, 0.006454388273598899, 0.014048814707233721, 0.0273633546417487, 0.04769183703790241, 0.07438130968834596, 0.10380747999523195, 0.12963985398596017, 0.1448750088982214] + [0.1469012] * 32 + [0.1448750088982214, 0.12963985398596017, 0.10380747999523195, 0.07438130968834596, 0.04769183703790241, 0.0273633546417487, 0.014048814707233721, 0.006454388273598899, 0.002653478346981973, 0.0009761601314482508],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_Y90_Q_wf": {
            "type": "arbitrary",
            "samples": [0.00044312470379322073, 0.0012045378300624087, 0.0029299484784956835, 0.006377413556680184, 0.012421505478229568, 0.021649553674581108, 0.03376515262357592, 0.04712306653639073, 0.05884958834786258, 0.06576553716634542] + [0.06668532] * 32 + [0.06576553716634542, 0.05884958834786258, 0.04712306653639073, 0.03376515262357592, 0.021649553674581108, 0.012421505478229568, 0.006377413556680184, 0.0029299484784956835, 0.0012045378300624087, 0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
        "q12_8_mY90_Q_wf": {
            "type": "arbitrary",
            "samples": [-0.00044312470379322073, -0.0012045378300624087, -0.0029299484784956835, -0.006377413556680184, -0.012421505478229568, -0.021649553674581108, -0.03376515262357592, -0.04712306653639073, -0.05884958834786258, -0.06576553716634542] + [-0.06668532] * 32 + [-0.06576553716634542, -0.05884958834786258, -0.04712306653639073, -0.03376515262357592, -0.021649553674581108, -0.012421505478229568, -0.006377413556680184, -0.0029299484784956835, -0.0012045378300624087, -0.00044312470379322073],
            "is_overridable": False,
            "max_allowed_error": 0.0001,
        },
    },
    "digital_waveforms": {
        "ON": {
            "samples": [(1, 0)],
        },
    },
    "integration_weights": {
        "integW_cos_rr1": {
            "cosine": [(0.1975375761873655, 2400)],
            "sine": [(-0.9802953157054362, 2400)],
        },
        "integW_sin_rr1": {
            "cosine": [(0.9802953157054362, 2400)],
            "sine": [(0.1975375761873655, 2400)],
        },
        "integW_minus_sin_rr1": {
            "cosine": [(-0.9802953157054362, 2400)],
            "sine": [(-0.1975375761873655, 2400)],
        },
        "integW_cos_rr2": {
            "cosine": [(-0.9270072224269928, 2000)],
            "sine": [(-0.37504347690393414, 2000)],
        },
        "integW_sin_rr2": {
            "cosine": [(0.37504347690393414, 2000)],
            "sine": [(-0.9270072224269928, 2000)],
        },
        "integW_minus_sin_rr2": {
            "cosine": [(-0.37504347690393414, 2000)],
            "sine": [(0.9270072224269928, 2000)],
        },
        "integW_cos_rr3": {
            "cosine": [(-0.5876299213481043, 3600)],
            "sine": [(-0.8091298261320125, 3600)],
        },
        "integW_sin_rr3": {
            "cosine": [(0.8091298261320125, 3600)],
            "sine": [(-0.5876299213481043, 3600)],
        },
        "integW_minus_sin_rr3": {
            "cosine": [(-0.8091298261320125, 3600)],
            "sine": [(0.5876299213481043, 3600)],
        },
        "integW_cos_rr4": {
            "cosine": [(-0.05395681831328809, 3600)],
            "sine": [(-0.9985432698473846, 3600)],
        },
        "integW_sin_rr4": {
            "cosine": [(0.9985432698473846, 3600)],
            "sine": [(-0.05395681831328809, 3600)],
        },
        "integW_minus_sin_rr4": {
            "cosine": [(-0.9985432698473846, 3600)],
            "sine": [(0.05395681831328809, 3600)],
        },
        "integW_cos_rr5": {
            "cosine": [(-0.6153863701791713, 2800)],
            "sine": [(0.7882256119904402, 2800)],
        },
        "integW_sin_rr5": {
            "cosine": [(-0.7882256119904402, 2800)],
            "sine": [(-0.6153863701791713, 2800)],
        },
        "integW_minus_sin_rr5": {
            "cosine": [(0.7882256119904402, 2800)],
            "sine": [(0.6153863701791713, 2800)],
        },
        "integW_cos_rr6": {
            "cosine": [(0.9404899467342636, 2800)],
            "sine": [(-0.33982151210860984, 2800)],
        },
        "integW_sin_rr6": {
            "cosine": [(0.33982151210860984, 2800)],
            "sine": [(0.9404899467342636, 2800)],
        },
        "integW_minus_sin_rr6": {
            "cosine": [(-0.33982151210860984, 2800)],
            "sine": [(-0.9404899467342636, 2800)],
        },
        "integW_cos_rr7": {
            "cosine": [(0.8157137790818908, 3200)],
            "sine": [(0.5784557291754835, 3200)],
        },
        "integW_sin_rr7": {
            "cosine": [(-0.5784557291754835, 3200)],
            "sine": [(0.8157137790818908, 3200)],
        },
        "integW_minus_sin_rr7": {
            "cosine": [(0.5784557291754835, 3200)],
            "sine": [(-0.8157137790818908, 3200)],
        },
        "integW_cos_rr8": {
            "cosine": [(0.8416630519706616, 2000)],
            "sine": [(-0.5400030619796812, 2000)],
        },
        "integW_sin_rr8": {
            "cosine": [(0.5400030619796812, 2000)],
            "sine": [(0.8416630519706616, 2000)],
        },
        "integW_minus_sin_rr8": {
            "cosine": [(-0.5400030619796812, 2000)],
            "sine": [(-0.8416630519706616, 2000)],
        },
    },
    "mixers": {
        "mixer_q1": [{'intermediate_frequency': 386784380.0, 'lo_frequency': 4700000000.0, 'correction': (1.0236070453213617, 0.08572239907421268, 0.08783950028446405, 0.9989361431935753)}],
        "mixer_rr1": [{'intermediate_frequency': 22665000.0, 'lo_frequency': 7388529000.0, 'correction': (1.0362739520394184, 0.1694157628041169, 0.16806191786288155, 1.0446217935108408)}],
        "mixer_q2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (1.0444961290328922, 0.06583338698039459, 0.07074813790071237, 0.9719367873490588)}],
        "mixer_rr2": [{'intermediate_frequency': 18800000.0, 'lo_frequency': 7388529000.0, 'correction': (1.1753568624073445, -0.1132445158954439, -0.14678881566699906, 0.9067633544347183)}],
        "mixer_q3": [{'intermediate_frequency': 372844133.0, 'lo_frequency': 4700000000.0, 'correction': (0.9716500277595905, -0.007498877298823346, -0.0070725332772443705, 1.030222700967818)}],
        "mixer_rr3": [{'intermediate_frequency': 43934000.0, 'lo_frequency': 7337596000.0, 'correction': (1.0656321623237386, -0.09872454699397955, -0.10843515817371514, 0.9702024164440017)}],
        "mixer_q4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (1.0184918793231268, 0.12360451516601981, 0.12273714898578643, 1.0256894182774456)}],
        "mixer_rr4": [{'intermediate_frequency': 20200000.0, 'lo_frequency': 7337596000.0, 'correction': (1.0819225500106364, -0.10026910802347513, -0.11316000478976894, 0.9586727151663961)}],
        "mixer_q5": [{'intermediate_frequency': 321812452.0, 'lo_frequency': 4700000000.0, 'correction': (1.013073268410779, 0.06955989519263533, 0.07036171113358658, 1.0015286615091483)}],
        "mixer_rr5": [{'intermediate_frequency': 18480000.0, 'lo_frequency': 7381058000.0, 'correction': (0.9223695069723006, 0.06174919416041147, 0.051627611515804084, 1.1031998595604318)}],
        "mixer_q6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (0.9958175654323856, 0.06271935271120836, 0.061482063944807264, 1.015857782172677)}],
        "mixer_rr6": [{'intermediate_frequency': 20294000.0, 'lo_frequency': 7381058000.0, 'correction': (0.991618959451214, 0.2878309591586392, 0.23602971047008225, 1.2092487663959264)}],
        "mixer_q7": [{'intermediate_frequency': 125957720.0, 'lo_frequency': 4700000000.0, 'correction': (0.9531282230165004, 0.04084422885368196, 0.03684101032608277, 1.0566970591527876)}],
        "mixer_rr7": [{'intermediate_frequency': 20544000.0, 'lo_frequency': 7381058000.0, 'correction': (1.433221002403429, 0.035912548247809734, 0.06669473246021809, 0.7717343859095386)}],
        "mixer_q8": [{'intermediate_frequency': -140337100.0, 'lo_frequency': 4300000000.0, 'correction': (0.9501664441395031, 0.05850250509417677, 0.0521698803260484, 1.0655021037269372)}],
        "mixer_rr8": [{'intermediate_frequency': 20000000.0, 'lo_frequency': 7395117500.0, 'correction': (1.4323943156170444, 0.032550787359555716, 0.060451462239174865, 0.7712892468707166)}],
        "mixer_cr_c1t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (1.0028048404625798, 0.05428708474480452, 0.054116798179439, 1.0059603152459933)}],
        "mixer_cr_c1t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (1.0035545076977206, 0.06183707871514085, 0.0615772911382139, 1.007788389848914)}],
        "mixer_cr_c1t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (1.003347752519738, 0.054374655796432, 0.05426086251524492, 1.0054519253551555)}],
        "mixer_cr_c3t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (0.9941242611207217, 0.03688402759555214, 0.036304000520180894, 1.0100073312912645)}],
        "mixer_cr_c3t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (0.9924270368118341, 0.03533658614774343, 0.03467305253814176, 1.0114189814431196)}],
        "mixer_cr_c3t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (1.000517709100806, 0.040676900393086524, 0.04051896463857211, 1.0044175500938168)}],
        "mixer_cr_c5t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (0.9922471331276873, 0.05081242150795721, 0.04964643131256334, 1.0155509315689217)}],
        "mixer_cr_c5t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (0.9839932556525414, 0.05317564250801031, 0.05105143646936771, 1.0249363624521883)}],
        "mixer_cr_c5t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (0.9898378311367794, 0.051560209338117856, 0.050120314119192856, 1.0182746593093936)}],
        "mixer_q12_1": [{'intermediate_frequency': 116063819.0, 'lo_frequency': 4700000000.0, 'correction': (0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035)}],
        "mixer_q12_2": [{'intermediate_frequency': 12572432.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_3": [{'intermediate_frequency': 102246113.0, 'lo_frequency': 4700000000.0, 'correction': (1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166)}],
        "mixer_q12_4": [{'intermediate_frequency': -21093907.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_5": [{'intermediate_frequency': 51366333.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_6": [{'intermediate_frequency': -146606483.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_7": [{'intermediate_frequency': -131548483.0, 'lo_frequency': 4700000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_q12_8": [{'intermediate_frequency': -204595000.0, 'lo_frequency': 4300000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_1": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (0.9879960797958184, -0.0007066848216332311, -0.0006897178244307592, 1.0123006955795035)}],
        "mixer_stark_2": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_3": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (1.0273079048111275, 0.006487487757209508, 0.006840920579384885, 0.9742325434139166)}],
        "mixer_stark_4": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_5": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_6": [{'intermediate_frequency': 10000000.0, 'lo_frequency': 4770000000.0, 'correction': (1.0059032449415808, -0.017629670731559466, -0.017821119749575846, 0.9950970110365455)}],
        "mixer_stark_7": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_stark_8": [{'intermediate_frequency': 40000000.0, 'lo_frequency': 40000000000.0, 'correction': (1.001039130070015, -0.05031974895634691, -0.05004715828565603, 1.0064914661706206)}],
        "mixer_cr_ac_c1t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c1t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c1t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c3t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c3t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c3t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c5t2": [{'intermediate_frequency': 281272650.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c5t4": [{'intermediate_frequency': 260657535.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
        "mixer_cr_ac_c5t6": [{'intermediate_frequency': 148637621.0, 'lo_frequency': 4700000000.0, 'correction': (1, 0, 0, 1)}],
    },
}


