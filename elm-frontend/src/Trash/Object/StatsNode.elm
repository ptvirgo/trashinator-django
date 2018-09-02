-- Do not manually edit this file, it was auto-generated by Graphqelm
-- https://github.com/dillonkearns/graphqelm


module Trash.Object.StatsNode exposing (..)

import Graphqelm.Field as Field exposing (Field)
import Graphqelm.Internal.Builder.Argument as Argument exposing (Argument)
import Graphqelm.Internal.Builder.Object as Object
import Graphqelm.Internal.Encode as Encode exposing (Value)
import Graphqelm.OptionalArgument exposing (OptionalArgument(Absent))
import Graphqelm.SelectionSet exposing (SelectionSet)
import Json.Decode as Decode
import Trash.InputObject
import Trash.Interface
import Trash.Object
import Trash.Scalar
import Trash.Union


{-| Select fields to build up a SelectionSet for this object.
-}
selection : (a -> constructor) -> SelectionSet (a -> constructor) Trash.Object.StatsNode
selection constructor =
    Object.selection constructor


site : SelectionSet decodesTo Trash.Object.SiteStatsNode -> Field decodesTo Trash.Object.StatsNode
site object =
    Object.selectionField "site" [] object identity


user : SelectionSet decodesTo Trash.Object.UserStatsNode -> Field decodesTo Trash.Object.StatsNode
user object =
    Object.selectionField "user" [] object identity
