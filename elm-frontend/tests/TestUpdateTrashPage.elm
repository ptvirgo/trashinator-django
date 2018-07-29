module TestUpdateTrashPage exposing (..)

import Expect exposing (Expectation)
import Fuzz exposing (Fuzzer, int, intRange, list, string)
import Test exposing (..)

import Date

import Models exposing (..)
import UpdateTrashPage exposing (..)


testTrash : Trash
testTrash = { date = Date.fromTime 1532750209000, amount = Gallons 0 }

testPage : TrashPage
testPage = { trash = Just testTrash, error = Nothing }

suite : Test
suite = describe "Test UpdateRecordPage"
    [ fuzz (intRange 0 10) "ChangeAmount changes amount of trash" <| \i ->
        let txt = toString i
            x = toFloat i
            newPage = { testPage | trash = Just
                                    { testTrash | amount = Gallons x }}
        in Expect.equal
            ( updateTrashPage (ChangeAmount txt) testPage )
            ( newPage, Cmd.none )

    , fuzz (intRange -10 -1) "ChangeAmount rejects numbers < 0" <| \i ->
        let txt = toString i
            newPage = { testPage | error = Just "Amount must be 0 or more" }
        in Expect.equal
            ( updateTrashPage (ChangeAmount txt) testPage )
            ( newPage, Cmd.none)

    , test "ChangeAmount rejects text strings" <| \_ ->
        let newPage = { testPage | error = Just "Amount must be a number" }
        in Expect.equal
            ( updateTrashPage (ChangeAmount "oops") testPage )
            ( newPage, Cmd.none )
    ]
